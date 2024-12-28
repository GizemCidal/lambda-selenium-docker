
### README

## **Selenium Web Scraping on AWS Lambda**

This project demonstrates how to scrape text content from web pages using Selenium in an AWS Lambda environment. It is designed to extract content from the page [Well-being on Wikipedia](https://en.wikipedia.org/wiki/Well-being) and save the results to an AWS S3 bucket in Parquet format.

---

### **Features**
- **Web Scraping with Selenium:** Uses a headless Chrome browser to extract text content from web pages.
- **AWS Integration:** Stores the scraped data as a Parquet file in an S3 bucket.
- **Scalable:** Designed to run in AWS Lambda, making it suitable for serverless deployments.

---

### **Setup Instructions**

1. **AWS Configuration:**
   - Set up environment variables:
     - `REGION_NAME`: Your AWS region (e.g., `us-east-1`).
     - `BUCKET_NAME`: The name of your target S3 bucket.

2. **Build Docker Image:**
   - Use the provided `Dockerfile` to build a Lambda-compatible image:
     ```bash
     docker build -t selenium-lambda .
     ```

3. **Deploy to AWS Lambda:**
   - Push the Docker image to AWS Elastic Container Registry (ECR).
   - Create an AWS Lambda function and link it to the Docker image.

4. **Run the Function:**
   - Trigger the Lambda function using a test event or an API gateway.
   - The extracted text will be saved to your S3 bucket.

---

### **Tech Stack**
- **Python 3.11:** Programming language for the Lambda function.
- **Selenium:** Web automation framework for scraping.
- **AWS Lambda:** Serverless function runtime.
- **AWS S3:** Storage service for the scraped data.

---

### **Example Output**
- The extracted content from [Well-being on Wikipedia](https://en.wikipedia.org/wiki/Well-being) is stored in S3 as a Parquet file, accessible with the generated key.

---

### **Contact**
Feel free to reach out for support or to share feedback! 😊
