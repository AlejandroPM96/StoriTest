import os
import csv
import smtplib
import json
import requests
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pymongo import MongoClient
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MONGO_URL = os.getenv("MONGO_URL")
USER = "AlejandroPM"

def process_transactions(file_path):
    transactions = []

    # Read transactions from CSV file
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transactions.append(row)

    # Group transactions by month
    transactions_by_month = defaultdict(list)
    for transaction in transactions:
        date = datetime.strptime(transaction['Date'], '%m/%d')
        month = date.strftime('%B')
        transactions_by_month[month].append(transaction)

    # Calculate total balance, number of transactions, and average credit/debit amounts
    summary = {
        'Total Balance': 0,
        'Number of Transactions': {},
        'Average Credit Amount': {},
        'Average Debit Amount': {}
    }
    total_balance = 0
    total_credit = 0
    total_debit = 0
    num_credit_transactions = 0
    num_debit_transactions = 0
    for month, month_transactions in transactions_by_month.items():
        for transaction in month_transactions:
            amount = float(transaction['Transaction'])
            total_balance += amount
            if amount > 0:
                total_credit += amount
                num_credit_transactions += 1
            else:
                total_debit += amount
                num_debit_transactions += 1

        num_transactions = len(month_transactions)

        summary['Number of Transactions'][month] = num_transactions

    summary['Total Balance'] += total_balance
    summary['Average Credit Amount'] = total_credit / num_credit_transactions
    summary['Average Debit Amount'] = total_debit / num_debit_transactions

    return summary, transactions

def save_to_mongodb(transactions):
    # Connect to MongoDB
    client = MongoClient(MONGO_URL)
    db = client["MyPlayground"]
    collection = db["transactions"]

    # Save transactions to MongoDB
    collection.insert_one({'user':USER, 'transactions': transactions})

def send_email(summary, transactions, receiver_email):
    # Initializing SMTP details
    sender_email = SMTP_EMAIL
    sender_password = SMTP_PASSWORD
    receiver_email = receiver_email
    USER = receiver_email
    subject = "Transaction Summary"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    message = MIMEMultipart('alternative')
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Logo image path
    image_path = 'https://mylilbuckettest.s3.us-east-2.amazonaws.com/logo.png'
    csv_file_path = 'txns.csv'

    # Create the email message with summary, transactions table, and logo image from file

    body = f"<html><body>"
    
    # Add total credit and debit in two columns
    body += "<div style='display: flex; justify-content: space-between;'>"
    body += f"<div style='flex: 1;'><h2>Total balance</h2><p>${summary['Total Balance']}</p></div>"
    body += f"<div style='flex: 1; margin-left: 50px;'><h2>Avarage Credit</h2><p>${summary['Average Credit Amount']}</p></div>"
    body += f"<div style='flex: 1; margin-left: 50px;'><h2>Avarage Debit</h2><p>${summary['Average Debit Amount']}</p></div>"
    body += "</div>"
    
    # Number of transactions
    body += "<h1>Transactions</h1>"
    body += "<div style='display: flex; justify-content: space-between;'>"
    for month in summary['Number of Transactions']:
        body += f"<div style='flex: 1; margin-left: 25px;'><h2>{month}: {summary['Number of Transactions'][month]}</h2></div>"
    body += "</div>"
    
    body += "<h2>Transactions</h2>"
    
    # Add transactions table
    table_header = "<tr>" + "".join([f"<th>{header}</th>" for header in transactions[0].keys()]) + "</tr>"
    body += f"<table border='1'>{table_header}"
    for transaction in transactions:
        row = "<tr>" + "".join([f"<td>{value}</td>" for value in transaction.values()]) + "</tr>"
        body += row
    body += "</table>"
    body += "<img src=\"cid:Mailtrapimage\" width=\"400\" height=\"200\">"
    body += "</body></html>"

    # Adding image
    fp = open('logo.png', 'rb')
    image = MIMEImage(fp.read())
    fp.close()
    
    image.add_header('Content-ID', '<Mailtrapimage>')
    message.attach(image)
    
    message.attach(MIMEText(body, 'html'))
    # Attach csv
    with open(csv_file_path, 'rb') as csv_file:
        csv_attachment = MIMEApplication(csv_file.read(), name='txns.csv')
        csv_attachment.add_header('Content-Disposition', 'attachment', filename='txns.csv')
        message.attach(csv_attachment)

    # Save transactions to MongoDB
    # save_to_mongodb(transactions)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

#Locally run the script 
# if __name__ == "__main__":
#     file_path = "txns.csv"

#     # Process transactions
#     summary, transactions = process_transactions(file_path)

#     # Send summary email with transactions table
#     send_email(summary, transactions, "your-email@example.com")
    
# Lambda Function handler
def lambda_handler(event, context):
    body = json.loads(event["body"])
    receiver_email = body.get("receiver_email", "default@email.com")
    try:
        summary, transactions = process_transactions('txns.csv')
        # Send summary email with transactions table
        send_email(summary, transactions, receiver_email)
    except Exception as err:
        {
            "statusCode": 501,
            "body": json.dumps({"message": "There was an error sending the email", "error": err})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Email sent successfully!"})
    }