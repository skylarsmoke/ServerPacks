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



hostName = "localhost"
serverPort = 8080
serverVersion = "v0.2.8"
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

    
def verify_license_key(licenseKey):
    sql_connection = sqlite3.connect("SynergyLicenseKey.db");
    cur = sql_connection.cursor()

    data = cur.execute(f"SELECT * FROM LICENSEKEYS WHERE LicenseKey = '{licenseKey}'")

    # if rows return it is a valid license key
    for row in data:
        sql_connection.close()
        return True

    sql_connection.close()
    return False
    
    
def generate_license_key():
    # Using random.choice to select characters from uppercase letters and digits
    key = ''.join([choice(ascii_uppercase + digits) for _ in range(7)]) + '-' + \
          ''.join([choice(ascii_uppercase + digits) for _ in range(7)]) + '-' + \
          ''.join([choice(ascii_uppercase + digits) for _ in range(7)])
    
    return key

class SynergyBassServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = post_data.decode('utf-8').split('&')
        print(request_data)

        if verify_product(request_data[0][8:]) and verify_email(request_data[1][6:]):
            responseData = KeyGen.generateKey(request_data[4][5:])
            response = bytes(f'<MESSAGE message="Success! Valid License Key"><KEY>{responseData}</KEY></MESSAGE>', "utf-8")
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
