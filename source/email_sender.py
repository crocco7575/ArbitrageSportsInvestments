import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
from scraper import scrapeOdds, url, bet_amount

def send_arbitrage_email(sender_email, sender_password, recipient_email):
    # First run the scraper to generate the CSV
    scrapeOdds(url)
    
    # Read the CSV file that was generated
    df = pd.read_csv("arbitrage_opportunities.csv")
    
    # Calculate summary metrics
    total_profit = df['Profit'].sum()
    total_return_percentage = (total_profit / bet_amount) * 100

    # Create email content
    msg = MIMEMultipart()
    msg['Subject'] = 'Arbitrage Opportunities Report'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Create email body
    body = f"""
    Daily Arbitrage Opportunities Report
    
    Total Profit This Batch: ${total_profit:.2f}
    Total Percent Return: {total_return_percentage:.2f}%
    
    Full details attached in CSV.
    """
    msg.attach(MIMEText(body, 'plain'))

    # Attach the CSV file
    with open("arbitrage_opportunities.csv", 'rb') as f:
        csv_attachment = MIMEApplication(f.read(), _subtype='csv')
        csv_attachment.add_header('Content-Disposition', 'attachment', 
                                filename='arbitrage_opportunities.csv')
        msg.attach(csv_attachment)

    # Send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
    send_arbitrage_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL)
if __name__ == "__main__":
    # Replace these with your email credentials
    SENDER_EMAIL = "cameronrocco75@gmail.com"
    SENDER_PASSWORD = "3647Cameron"  # Use App Password for Gmail
    RECIPIENT_EMAIL = "cameronrocco75@gmail.com"
    
    send_arbitrage_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL)

    print("SENT!")