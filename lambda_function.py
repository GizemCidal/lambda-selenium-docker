import io
import logging
import os
import time

import boto3
import pandas as pd
from botocore.client import Config as BotoCoreConfig
from botocore.exceptions import BotoCoreError, ClientError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


logger = setup_logger()


class AWSConfig:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = None
        self.configure_client()

    def configure_client(self):
        try:
            client_config = BotoCoreConfig(
                connect_timeout=1, read_timeout=1, retries={"max_attempts": 3}
            )

            region_name = os.getenv("REGION_NAME")
            self.bucket_name = os.getenv("BUCKET_NAME")
            if not region_name or not self.bucket_name:
                raise EnvironmentError(
                    "REGION_NAME or BUCKET_NAME environment variables are not set"
                )

            boto3_session = boto3.session.Session(region_name=region_name)
            self.s3_client = boto3_session.client(
                "s3", region_name=region_name, config=client_config
            )
            logger.info("AWSConfig initialized successfully.")
        except (BotoCoreError, ClientError, Exception) as e:
            logger.error(f"An error occurred with Boto3 or Botocore: {e}")
            raise


class S3Handler:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    def upload_parquet_to_s3(self, dataframe, bucket, key):
        try:
            buffer = io.BytesIO()
            dataframe.to_parquet(buffer, index=False)
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=buffer.getvalue(),
                ContentType="application/octet-stream",
            )
        except Exception as e:
            logger.error(f"Error uploading Parquet file to S3: {e}")
            raise


class WebDriverManager:
    @staticmethod
    def initialize_driver():
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")  # Headless modda çalıştırır
            chrome_options.add_argument(
                "--no-sandbox"
            )  # Sandbox modunu devre dışı bırakır
            chrome_options.add_argument(
                "--disable-dev-shm-usage"
            )  # Paylaşılan bellek kullanımını devre dışı bırakır
            chrome_options.add_argument(
                "--disable-gpu"
            )  # GPU işlemlerini devre dışı bırakır
            chrome_options.add_argument(
                "--disable-software-rasterizer"
            )  # Yazılım rasterizerını devre dışı bırakır
            chrome_options.add_argument(
                "--disable-extensions"
            )  # Tarayıcı uzantılarını devre dışı bırakır
            chrome_options.add_argument(
                "--disable-background-networking"
            )  # Arka plan ağ işlemlerini devre dışı bırakır
            chrome_options.add_argument(
                "--disable-default-apps"
            )  # Varsayılan uygulamaları devre dışı bırakır
            chrome_options.add_argument(
                "--disable-sync"
            )  # Tarayıcı eşitlemesini devre dışı bırakır
            chrome_options.add_argument(
                "--disable-web-security"
            )  # Web güvenlik ayarlarını devre dışı bırakır
            chrome_options.add_argument(
                "--disable-features=VizDisplayCompositor"
            )  # Görsel Compositor'ı devre dışı bırakır
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument(
                "--single-process"
            )  # Tek işlem modunda çalıştırır
            chrome_options.add_argument(
                "--remote-debugging-port=9222"
            )  # Uzaktan hata ayıklama için port
            chrome_options.add_argument(
                "--no-first-run"
            )  # İlk çalıştırma deneyimini devre dışı bırakır
            chrome_options.add_argument(
                "--ignore-certificate-errors"
            )  # Sertifika hatalarını görmezden gelir
            chrome_options.add_argument(
                "--start-maximized"
            )  # Tarayıcıyı tam ekran başlatır
            chrome_options.binary_location = "/opt/chrome/chrome"

            service = Service(
                executable_path="/opt/chrome-driver/chromedriver",
                service_log_path="/tmp/chromedriver.log",
            )
            logger.info(f"Setting ChromeDriver path: {service.path}")

            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("WebDriver initialized successfully.")
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise e


class DiskSpaceChecker:
    @staticmethod
    def check_disk_space():
        free_space_mb = (
            os.statvfs("/tmp").f_bavail * os.statvfs("/tmp").f_frsize / 1024 / 1024
        )
        logger.info(f"Available disk space in /tmp: {free_space_mb:.2f} MB")
        if free_space_mb < 500:
            raise RuntimeError("Insufficient disk space in /tmp.")


def lambda_handler(event, context):
    try:
        # AWS Configuration
        aws_config = AWSConfig(state="prod")
        s3_handler = S3Handler(aws_config.s3_client)

        # Check Disk Space
        DiskSpaceChecker.check_disk_space()

        # Initialize WebDriver
        driver = WebDriverManager.initialize_driver()

        # Process Well-being page
        url = "https://en.wikipedia.org/wiki/Well-being"
        driver.get(url)

        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info(f"Page loaded successfully: {url}")

        # Extract main content
        try:
            main_content = driver.find_element(By.ID, "bodyContent")
            paragraphs = main_content.find_elements(By.TAG_NAME, "p")
            extracted_text = "\n".join([p.text for p in paragraphs if p.text.strip()])

            if not extracted_text:
                raise ValueError("No text content extracted from the page.")

            result = {"url": url, "text": extracted_text}
            logger.info("Text extracted successfully.")
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            result = {"url": url, "error": str(e)}

        # Save results to S3
        df = pd.DataFrame([result])
        logger.info(f"Dataframe created: {df.head()}")
        s3_key = f"wellbeing_page_content_{int(time.time())}.parquet"
        s3_handler.upload_parquet_to_s3(df, aws_config.bucket_name, s3_key)

        logger.info(f"Results saved to S3 at key: {s3_key}")
        return {"statusCode": 200, "body": f"Data saved to S3 at key: {s3_key}"}

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {"statusCode": 500, "body": "Internal Server Error"}
    finally:
        if "driver" in locals():
            driver.quit()
            logger.info("WebDriver closed.")
