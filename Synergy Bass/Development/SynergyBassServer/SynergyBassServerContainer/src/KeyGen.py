import time
from xml.etree.ElementTree import XML
from Crypto.PublicKey import RSA
from Crypto.Util.number import long_to_bytes

# Variables
PRODUCT_ID = "SynergyBass"
EMAIL = "client@rumorvst.ai"
USER = "testuser"
DATE = time.strftime("%d %b %Y %I:%M:%S%p")
#MACHINE = "W7F9724C94"
TIME = hex(round(time.time() * 1000))

PRIVATE_KEY_PART_1 = int("279808e40cef4350640026c8739e7201826d002cec7e260f3d16d0cf786842f1", 16)
PRIVATE_KEY_PART_2 = int("602815978d207ee7ce4982c23d5c39729da90af57b850863165936256e3b7227", 16)

# Helper Function
def apply_to_value(message, key_part1, key_part2):
    result = 0
    value = int(message[::-1].encode('utf-8').hex(), 16)
    while value != 0:
        result *= key_part2
        value, remainder = divmod(value, key_part2)
        result += pow(remainder, key_part1, key_part2)
    return hex(result)[2:]

def generateKey(machineID):
    # Create the XML 
    xml_string = f'<key user="{USER}" email="{EMAIL}" mach="{machineID}" app="{PRODUCT_ID}" date="{TIME}"/>'
    encrypted_xml = "#" + apply_to_value(xml_string, PRIVATE_KEY_PART_1, PRIVATE_KEY_PART_2)
    
    # Output the encrypted XML data
    xml_data = [encrypted_xml[i:i+70] for i in range(0, len(encrypted_xml), 70)]
    
    keyFile = ""

    for line in xml_data:
        keyFile += line

    return keyFile









