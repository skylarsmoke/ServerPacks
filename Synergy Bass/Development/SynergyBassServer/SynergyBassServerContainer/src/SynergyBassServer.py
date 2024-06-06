'''
Synergy Bass Server Code

Contains server side logic for issuing license keys and validating requests from client machines.

'''


from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import sqlite3
from random import choice
from string import ascii_uppercase, digits
from urllib import response

import KeyGen

'''
Database Schema

Table LICENSEKEYS

Columns
LicenseKey
Email
MachineNumber


'''


hostName = "localhost"
serverPort = 8080
serverVersion = "v0.6.4"
privateRSAKey = "279808e40cef4350640026c8739e7201826d002cec7e260f3d16d0cf786842f1,602815978d207ee7ce4982c23d5c39729da90af57b850863165936256e3b7227"
publick = "11,602815978d207ee7ce4982c23d5c39729da90af57b850863165936256e3b7227"

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

    
def verify_license_key(licenseKey, machineNumber):
    sql_connection = sqlite3.connect("SynergyLicenseKey.db");
    cur = sql_connection.cursor()

    data = cur.execute(f"SELECT * FROM LICENSEKEYS WHERE LicenseKey = '{licenseKey}'")

    # if rows return it is a valid license key
    for row in data:
        # if the machine number is different than the original registration, it is not valid
        if (row[2] != machineNumber):
            return [False, "mach"]
        sql_connection.close()
        return [True, ""]

    sql_connection.close()
    return [False, "inv"]
    
# inserts a new license key into the database
def insert_new_license(licenseKey, email, machineNumber):
    sql_connection = sqlite3.connect("SynergyLicenseKey.db");
    cur = sql_connection.cursor()

    data = cur.execute(f"INSERT INTO LICENSEKEYS VALUES ('{licenseKey}', '{email}', '{machineNumber}')")

    sql_connection.commit()
    sql_connection.close()
    
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

def verify_license_is_unique(licenseKey):
    sql_connection = sqlite3.connect("SynergyLicenseKey.db");
    cur = sql_connection.cursor()

    data = cur.execute(f"SELECT * FROM LICENSEKEYS WHERE LicenseKey = '{licenseKey}'")

    # if rows return it is not a unique license key
    for row in data:
        sql_connection.close()
        return False

    sql_connection.close()
    return True
    
# TODO: Create method of generating new keys and sending them to users

class SynergyBassServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = post_data.decode('utf-8').split('&')
        print(request_data)

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
    webServer = HTTPServer((hostName, serverPort), SynergyBassServer)
    print("Synergy Bass Server Pack - " + serverVersion + " - http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
