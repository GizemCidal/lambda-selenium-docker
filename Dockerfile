FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.11-x86_64

# Install necessary dependencies for Headless Chrome and Selenium
RUN yum install -y \
    mesa-libgbm nss alsa-lib libatk gtk3 \
    libXcomposite libXcursor libXdamage libXext libXi \
    libXrandr libXtst libXScrnSaver libxcb pango at-spi2-atk \
    unzip wget jq

# 1) CHROME İNDİRME (Chrome 117)
ARG CHROME_VERSION=117.0.5938.88
RUN curl -Lo /tmp/chrome.zip \
    https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chrome-linux64.zip && \
    mkdir -p /opt/chrome && \
    unzip -q /tmp/chrome.zip -d /opt/chrome && \
    ln -s /opt/chrome/chrome-linux64/chrome /opt/chrome/chrome && \
    rm -rf /tmp/chrome.zip

# 2) CHROMEDRIVER İNDİRME (ChromeDriver 117)
ARG CHROMEDRIVER_VERSION=117.0.5938.88
RUN curl -Lo /tmp/chromedriver.zip \
    https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    mkdir -p /opt/chrome-driver && \
    unzip -q /tmp/chromedriver.zip -d /opt/chrome-driver && \
    ln -s /opt/chrome-driver/chromedriver-linux64/chromedriver /opt/chrome-driver/chromedriver && \
    chmod +x /opt/chrome-driver/chromedriver && \
    rm -rf /tmp/chromedriver.zip

# 3) ENV PATH ve Ek Environment Variables
ENV PATH="/opt/chrome:${PATH}"
ENV PATH="/opt/chrome-driver:${PATH}"

ENV XDG_RUNTIME_DIR=/tmp
ENV HOME=/tmp
ENV TMP=/tmp
ENV TMPDIR=/tmp

# 4) pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy source code
COPY lambda_function.py .

# 6) CMD
CMD [ "lambda_function.lambda_handler" ]
