# AWS Lambda Function with Docker

This project demonstrates a Python script that processes transactions from a CSV file, generates a summary, and sends an email with the summary and transaction details as an HTML table. The script is designed to run as an AWS Lambda function inside a Docker image.

## Prerequisites

Make sure you have the following installed on your local machine:

- [Docker](https://www.docker.com/)
- [AWS CLI](https://aws.amazon.com/cli/)

## Local Development

To run the script locally:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/lambda-docker-example.git
    cd lambda-docker-example
    ```

2. **Create a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file with the following environment variables:**

    ```env
    SMTP_EMAIL=your-smtp-email@gmail.com
    SMTP_PASSWORD=your-smtp-password
    MONGO_URL=your-mongo-url
    ```

5. **Create a `txns.csv` file with your transaction data.**

6. **Run the script:**

    ```bash
    python your_script_name.py
    ```

## AWS Lambda Deployment

To deploy the script as an AWS Lambda function inside a Docker image:

1. **Build your Docker image:**

    ```bash
    docker build -t your-image-name .
    ```

2. **Push the image to your container registry:**

    ```bash
    docker tag your-image-name:latest your-registry-url/your-image-name:latest
    docker push your-registry-url/your-image-name:latest
    ```

3. **Create an AWS Lambda function using the container image.**

4. **Configure the Lambda function to use the provided container image URI.**

5. **Set up an API Gateway trigger for the Lambda function to allow HTTP POST requests.**

6. **Test the Lambda function by sending an HTTP POST request with a JSON payload:**

    ```json
    {
      "receiver_email": "your-email@example.com"
    }
    ```
