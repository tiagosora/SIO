import PyKCS11
from cryptography import x509
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash
from cryptography.hazmat.primitives import serialization


lib = '/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so'
pkcs11 = PyKCS11.PyKCS11Lib()
pkcs11.load(lib)
slot = pkcs11.getSlotList(tokenPresent=True)[0]

all_attributes = list(PyKCS11.CKA.keys())
#Filter attributes
all_attributes = [e for e in all_attributes if isinstance(e, int)]


session = pkcs11.openSession(slot)
session.login('1111') 

for obj in session.findObjects():
    attr = session.getAttributeValue(obj, all_attributes)
    attrDict = dict(list(zip(all_attributes, attr)))


    if attrDict[PyKCS11.CKA_CLASS] == PyKCS11.CKO_PRIVATE_KEY:
        if attrDict[PyKCS11.CKA_ID][0] == 69:     # signature
            private_key = obj

    if attrDict[PyKCS11.CKA_CLASS] == PyKCS11.CKO_CERTIFICATE:
        if attrDict[PyKCS11.CKA_ID][0] == 69:
            cert_obj = obj
            cert_der_data = bytes(cert_obj.to_dict()['CKA_VALUE'])

session.logout()

der_cert = x509.load_der_x509_certificate(cert_der_data, backend=db())

bytes_cert = der_cert.public_bytes(encoding=serialization.Encoding.PEM)

pem_cert = x509.load_pem_x509_certificate(bytes_cert)
print(bytes_cert)

with open('callers_certs/cert_8.pem', 'wb') as f:
    f.write(bytes_cert)
    f.close()