'''
Synergy Bass Server Code

Contains server side logic for issuing license keys and validating requests from client machines.

'''

# Standard Library Imports
import base64
import hashlib
import hmac
import json
import logging
import smtplib
import sys
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from platform import machine
from random import choice
from string import ascii_uppercase, digits
from urllib import response

# Third-Party Imports
import pyodbc
import pymysql
import sqlalchemy
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from google.cloud.sql.connector import Connector, IPTypes
import urllib

# Local Application Imports
import KeyGen

# Set up connection variables
instance_connection_name = "synergybassserver:us-central1:synergy-bass-licenses"
db_user = "sqlserver"
db_password = "Rumoraudioisdope1!"
db_name = "SynergyBassLicenses"

# Initialize the Cloud SQL Connector
connector = Connector()

# Create connection string
connection_string = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER=127.0.0.1,1433;"
    f"DATABASE={db_name};"
    f"UID={db_user};"
    f"PWD={db_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)


# create connection pool
pool = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")

hostName = "0.0.0.0"
serverPort = 8080
serverVersion = "v0.8.5"
privateRSAKey = "279808e40cef4350640026c8739e7201826d002cec7e260f3d16d0cf786842f1,602815978d207ee7ce4982c23d5c39729da90af57b850863165936256e3b7227"
publick = "11,602815978d207ee7ce4982c23d5c39729da90af57b850863165936256e3b7227"
shopify_secret = 'd2166fdd8ed38f7a74a4056d54f0bd39'


def verify_product(product):
    if product == "SynergyBass":
        return True
    else:
        return False
    
def verify_email(email):
    if email == "client%40rumorvst.ai":
        return True
    else:
        return False

# updates the machine number when the user first registers their license key
def update_machine_number(licenseKey, machineNumber):
    with pool.connect() as db_conn:
        sql = sqlalchemy.text(f"UPDATE tblLicenseKeys SET MachineNumber = '{machineNumber}' WHERE LicenseKey = '{licenseKey}'")
        result = db_conn.execute(sql)
        db_conn.commit()
        
        if result.rowcount != 1:
            return False
        
    
        db_conn.close()
    return True
    
# verifies whether or not a license key is valid
def verify_license_key(licenseKey, machineNumber):
    with pool.connect() as db_conn:
        sql = sqlalchemy.text(f"SELECT * FROM tblLicenseKeys WHERE LicenseKey = '{licenseKey.upper()}'")
        result = db_conn.execute(sql)

        for row in result.mappings():
            # first check if the machine number is populated
            if row["MachineNumber"] == "":
                if not update_machine_number(licenseKey, machineNumber):
                    return [False, "update_failed"]
            elif row["MachineNumber"] != machineNumber:
                # if the machine number is different than the original registration, it is not valid
                return [False, "mach"]
            return [True, ""]
    
        db_conn.close()
    return [False, "inv"]

    
# inserts a new license key into the database
def insert_new_license(licenseKey, email, machineNumber):
    with pool.connect() as db_conn:
        sql = sqlalchemy.text(f"INSERT INTO tblLicenseKeys VALUES ('{licenseKey.upper()}', '{email.lower()}', '{machineNumber}')")
        db_conn.execute(sql)
    
        db_conn.commit()
        db_conn.close()

# removes the machine number associated to a license key, this should never be called from a clients machine
def clear_machine_number(licenseKey):
    with pool.connect() as db_conn:
        sql = sqlalchemy.text(f"UPDATE tblLicenseKeys SET MachineNumber = '' WHERE LicenseKey = '{licenseKey.upper()}'")
        result = db_conn.execute(sql)
        db_conn.commit()
        
        if result.rowcount != 1:
            return False
    
    return True

def get_total_licenses():
    with pool.connect() as db_conn:
        sql = sqlalchemy.text("SELECT COUNT(*) FROM tblLicenseKeys")
        result = db_conn.execute(sql)
        
        rowCount = result.rowcount
    
        db_conn.close()
    return rowCount
    
# generates a random license key
def generate_license_key():
    # Using random.choice to select characters from uppercase letters and digits
    key = ''.join([choice(ascii_uppercase + digits) for _ in range(7)]) + '-' + \
          ''.join([choice(ascii_uppercase + digits) for _ in range(7)]) + '-' + \
          ''.join([choice(ascii_uppercase + digits) for _ in range(7)])
    
    if (verify_license_is_unique(key)):
        return key
    else:
        return generate_license_key()

# verifies whether a generated license key is unique
def verify_license_is_unique(licenseKey):
    with pool.connect() as db_conn:
        sql = sqlalchemy.text(f"SELECT * FROM tblLicenseKeys WHERE LicenseKey = '{licenseKey.upper()}'")
        result = db_conn.execute(sql)
        
        # if rows return it is not a unique license key
        if result.rowcount > 0:
            return False

    
    connector.close()
    return True
    
# wrapper function to execute all processes that must happen when a new license is purchased
def create_new_license(email):
    newLicenseKey = generate_license_key()
    insert_new_license(newLicenseKey, email, "")
    return newLicenseKey

# retrieves the license key for the given email
def get_license_from_email(email):
    with pool.connect() as db_conn:
        sql = sqlalchemy.text(f"SELECT LicenseKey FROM tblLicenseKeys WHERE Email = '{email.lower()}'")
        result = db_conn.execute(sql)
        
        # Fetch all the results
        rows = result.fetchall()
        
        # Extract the LicenseKey values from the rows and return them as a list
        license_keys = [row[0] for row in rows]
    
    return license_keys


def send_email(subject, content, toEmail, from_email, password):

    message = Mail(
        from_email='support@rumoraudio.com',
        to_emails=toEmail,
        subject = 'Thank you for your purchase!',
        html_content=content)

    try:
        sg = sendgrid.SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        logging.info('Email sent successfully')
    except Exception as e:
        print(e.message)
        logging.error(f'Error: {e}')

def send_license_key_email(email):
    newLicenseKey = create_new_license(email)
    
    subject = "Synergy Bass - Thank you for your purchase!"
    html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #2D2D30;
                color: white;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 100%;
                margin: auto;
                overflow: hidden;
            }
            .header {
                background: #6123FF;
                color: #FFFFFF;
                padding: 20px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .content {
                background: #1F1F21;
                color: #FFFFFF;
                padding: 20px;
                margin-top: 0px;
	            text-align: center;
            }
            .content h2 {
                color: #6123FF;
                font-size: 20px;
                text-align: center;
            }
            .content p {
                font-size: 16px;
                line-height: 1.5;
                color: white;
            }
            .rectangle {
                border: 2px solid #6123FF;
                padding: 15px;
                margin: 20px 0;
            }
            .buttons {
                margin: 20px 0;
            }
            .button {
                background-color: #6123FF;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
            }
            .footer {
                background: #6123FF;
                color: #ffffff;
                text-align: center;
                padding: 10px;
                margin-top: 0px;
            }
        </style>

        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>Thank you for your purchase!</h2>
                    <p>We can't wait to hear what you come up with! Below you can find your license key for activating Synergy Bass.</p>
                    <div class="rectangle">
                        <p>""" + newLicenseKey + """</p>
                    </div>
                    <div class="buttons">
                        <a href="https://www.example.com/mac-download" class="button" style="color: #FFFFFF; text-decoration: none">Download for Mac</a>
                        <a href="https://drive.google.com/uc?export=download&id=1TL89ym118KMCFy7YZkfrlBydATuzR9PS" class="button" style="color: #FFFFFF; text-decoration: none">Download for Windows</a>
                    </div>
                    <p>We hope you enjoy our plugin and if you have any questions or concerns please reach out!</p>
                    <p>Best regards,</p>
                    <p><strong>The Rumor Team</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Rumor LLC. All rights reserved.</p>
                    <p><a href="https://www.rumoraudio.com" style="color: #ffffff; text-decoration: none;">Visit our website</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
    to_email = email
    from_email = "support@rumoraudio.com"
    password = "zzlw zacj vyvl nqbn"
    
    send_email(subject, html_content, to_email, from_email, password)


class SynergyBassServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # logging.info("POST request received")
        # logging.info(f"Headers: {self.headers}")
        # logging.info(f"Body: {post_data}")
        
        hmac_header = self.headers.get('X-Shopify-Hmac-Sha256')

        # Check if the request is from Shopify
        if hmac_header:
            request_data = json.loads(post_data)
            email = request_data['email']
            
            logging.info(f"Email: {email}")

            # Handle Shopify specific logic
            response = bytes("Shopify webhook received", "utf-8")
            send_license_key_email(email)
            logging.info("Successful shopify webhook")
            

        else:
            # Handle other POST requests
            request_data = post_data.decode('utf-8').split('&')
            print(request_data)

            '''
            All code in this section is for maintenance requests from the admin tool
            '''
        
            if (request_data[0].find("#licenseKeyReset#") != -1):
                licenseKey = request_data[0][request_data[0].find(":") + 3:][0:23]
                print(f"Clearing machNumber for license key: {licenseKey}")
                machClear = clear_machine_number(licenseKey)
                if machClear:
                    response = bytes("Machine Number Cleared", "utf-8")
                else:
                    response = bytes("License Key Not Found", "utf-8")
            elif (request_data[0].find("#getTotals#") != -1):
                response = bytes(f"{get_total_licenses()}", "utf-8")
            elif (request_data[0].find("#newLicense#") != -1):
                email = request_data[0][request_data[0].find(":") + 3:][0:request_data[0].rfind('"') - 18]
                response = bytes(f"{create_new_license(email)}", "utf-8")
            elif (request_data[0].find("#getLicense#") != -1):
                email = request_data[0][request_data[0].find(":") + 3:][0:request_data[0].rfind('"') - 18]
                response = bytes(f"{get_license_from_email(email)}", "utf-8")
            else:
            
                '''
                All code in this section is for verifying license key requests from the client plugin
                '''

                #clear_machine_number(request_data[2][3:]); For testing
                verificationResults = verify_license_key(request_data[2][3:], request_data[4][5:])
        
                if verify_product(request_data[0][8:]) and verify_email(request_data[1][6:]) and verificationResults[0]:
                    responseData = KeyGen.generateKey(request_data[4][5:])
                    response = bytes(f'<MESSAGE message="Success! Valid License Key"><KEY>{responseData}</KEY></MESSAGE>', "utf-8")
                else:
                    if (verificationResults[1] == "mach"):
                        response = bytes('<ERROR error="This license key is registered to a different machine."></ERROR>', "utf-8")
                    else:
                        response = bytes('<ERROR error="Invalid License Key"></ERROR>', "utf-8")
        
        self.send_response(200)
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        
        self.wfile.write(response)
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

    webServer = HTTPServer((hostName, serverPort), SynergyBassServer)
    print("Synergy Bass Server Pack - " + serverVersion + " - http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
