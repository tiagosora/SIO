import _thread
import binascii

import PyKCS11
from cryptography import x509
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash


class PTeID:
    def __init__(self) -> None:
        self._lib = './cc/opensc-pkcs11.so'
        self.pkcs11 = PyKCS11.PyKCS11Lib()
        self.pkcs11.load(self._lib)
        self.slot = self.pkcs11.getSlotList(tokenPresent=True)[0]

        (self._private_key, self.cert) = self.get_info()

        self.public_key = self.cert.public_key()

    def open_session(self):
        session = self.pkcs11.openSession(self.slot)
        session.login('1111')
        return session

    def close_session(self, session):
        session.logout()

    def get_info(self):
        all_attributes = list(PyKCS11.CKA.keys())
        #Filter attributes
        all_attributes = [e for e in all_attributes if isinstance(e, int)]

        session = self.open_session()

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

        self.close_session(session)

        cert = x509.load_der_x509_certificate(cert_der_data, backend=db())

        return (private_key, cert)

    def signature(self, text):
        session = self.open_session()

        mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None)
        signature = bytes(session.sign(self._private_key, text, mechanism))

        self.close_session(session)

        return signature

    def validate_signature(self, text, signature):
        md = Hash(SHA1(), backend=db())
        md.update(text)
        digest = md.finalize()

        try:
            self.public_key.verify(
                signature,
                digest,
                PKCS1v15(),
                SHA1()
            )
            result = True
        except:
            result = False

        return result