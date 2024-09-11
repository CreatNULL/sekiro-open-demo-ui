# coding: utf-8

import os
try:
    import win32crypt
except ModuleNotFoundError:
    os.system('pip install win32crypt')


# Flag variables
CERT_STORE_PROV_SYSTEM = 0x0000000A
CERT_STORE_OPEN_EXISTING_FLAG = 0x00004000
CRYPT_STRING_BASE64HEADER = 0x00000000
CERT_SYSTEM_STORE_CURRENT_USER_ACCOUNT = 1<<16
X509_ASN_ENCODING = 0x00000001
CERT_STORE_ADD_REPLACE_EXISTING = 3
CERT_CLOSE_STORE_FORCE_FLAG = 0x00000001

# replace with your certificate file path
crtPath = "D:\\certificates\\cert_file.crt"

with open(crtPath,'r') as f:
    cert_str = f.read()

cert_byte = win32crypt.CryptStringToBinary(cert_str, CRYPT_STRING_BASE64HEADER)[0]
store = win32crypt.CertOpenStore(CERT_STORE_PROV_SYSTEM, 0, None, CERT_SYSTEM_STORE_CURRENT_USER_ACCOUNT|CERT_STORE_OPEN_EXISTING_FLAG, "ROOT")


try:
    store.CertAddEncodedCertificateToStore(X509_ASN_ENCODING, cert_byte, CERT_STORE_ADD_REPLACE_EXISTING)
finally:
    store.CertCloseStore(CERT_CLOSE_STORE_FORCE_FLAG)