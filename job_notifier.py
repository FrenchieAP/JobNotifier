import os
import time
import requests
import smtplib
import pickle
import base64
from bs4 import BeautifulSoup
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

# Configure your email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "yolomanswagmuffin@gmail.com"
EMAIL_PASSWORD = "Rootroot555!"
TO_EMAIL_ADDRESS = "anthony.pepino1@gmail.com"

# Path to your WebDriver executable
WEBDRIVER_PATH = "C:/Users/antho/OneDrive/Desktop/ChromeDriver/chromedriver.exe"

# URL of Cequint's careers page
CEQUINT_CAREERS_URL = "https://tnsi.wd1.myworkdayjobs.com/Search?locationRegionStateProvince=de9b48948ef8421db97ddf4ea206e931"

# Path to your 'credentials.json' file
CREDENTIALS_PATH = 'C:/Users/antho/OneDrive/Desktop/ClientSecret/client_secret_461612581699-evtidhn36qivg4bsbgu7mblvu4s57gss.apps.googleusercontent.com.json'

# Function to load Google API credentials
def get_google_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, ['https://www.googleapis.com/auth/gmail.send'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Function to check for new jobs with the keywords "engineer", etc.
def check_for_new_jobs(driver):
    driver.get(CEQUINT_CAREERS_URL)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-automation-id="jobTitle"].css-19uc56f'))
        )
        job_listings = driver.find_elements(By.CSS_SELECTOR, 'a[data-automation-id="jobTitle"].css-19uc56f')
    except TimeoutException:
        job_listings = []

    new_jobs = []
    for job in job_listings:
        job_title = job.text.strip()
        if job_title not in seen_jobs and ("engineer" in job_title.lower() or "developer" in job_title.lower() or "QA" in job_title.lower() or "tester" in job_title.lower()):
            new_jobs.append(job_title)
            seen_jobs.add(job_title)

    return new_jobs

# Function to send email notifications
def send_email_notification(creds, new_jobs):
    msg = EmailMessage()
    msg.set_content("\n".join(new_jobs))

    msg["Subject"] = f"{len(new_jobs)} new job(s) with 'engineer' at Cequint"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL_ADDRESS

    service = build('gmail', 'v1', credentials=creds)
    raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    result = service.users().messages().send(userId="me", body={'raw': raw_msg}).execute()
    print(F'sent message to {TO_EMAIL_ADDRESS} Message Id: {result["id"]}')

# Initialize seen_jobs set
seen_jobs = set()

# Initialize WebDriver
options = ChromeOptions()
options.add_argument('--headless')  # Run the browser in headless mode (optional)
service = Service(executable_path=WEBDRIVER_PATH)
driver = Chrome(service=service, options=options)


# Main loop
while True:
    print("Checking for new jobs...")
    new_jobs = check_for_new_jobs(driver)
    if new_jobs:
        print("New jobs found:", new_jobs)
        creds = get_google_credentials()
        send_email_notification(creds, new_jobs)
    else:
        print("No new jobs found.")
    time.sleep(1000)  # Check every hour (change this value to your desired frequency)


driver.quit()
