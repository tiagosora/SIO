import base64
import datetime as dt
import pickle

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class Logger:
    
    def __init__(self):
        self.cntr = 0
        self.filename = f"bingolog-{dt.datetime.now():%Y-%m-%d_%H-%M-%S}.txt"

    @property
    def prev_entry(self):
        try:
            with open("logs/" + self.filename, 'r') as f:
                lines = f.readlines()
                return lines[-1].strip().encode('utf-8')
        except:
            return b''
    
    def log(self, msg, signature):
        id = str(self.count())
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        hash_prev_entry = base64.b64encode(self.hash(self.prev_entry)).decode('utf-8')
        text = base64.b64encode(pickle.dumps(msg)).decode('utf-8')
        signature = base64.b64encode(signature).decode('utf-8')
        log = id + ', ' + timestamp + ', ' + hash_prev_entry + ', ' + text + ', ' + signature
        
        with open("logs/" + self.filename, 'a') as f:
            f.write(log + '\n')

    def get_logs(self):
        with open("logs/" + self.filename, 'r') as f:
            logs = [l.strip() for l in f.readlines()]
        return logs
        
    def hash(self, data):
        h = hashes.Hash(hashes.SHA256())
        h.update(data)
        return h.finalize()

    def count(self):
        self.cntr += 1
        return self.cntr - 1

class LogReader:

    def __init__(self, filename=None):
        self.filename = filename

    def displayLogs(self, logs=None):
        if self.filename == None and logs == None:
            print("No filename set.")
            return
        
        if logs == None:
            with open("logs/" + self.filename, 'r') as f:
                lines = f.readlines()
        else:
            lines = logs
            
        for log in lines:
            logdt = log.split(', ')
            seq = logdt[0]
            ts = logdt[1]
            msg = pickle.loads(base64.b64decode(logdt[3].encode('utf-8')))
            print(" ", seq, ts, "-", msg)

        m = "Log order intact." if self.verifyLogOrder(lines) else "Log order tampered with!"
        print(m)

    def verifyLog(self, logidx, public_key, logs=None):
        if logs == None:
            with open("logs/" + self.filename, 'r') as f:
                line = f.readlines()[logidx].strip()
        else:
            line = logs[logidx].strip()
        
        msg = pickle.loads(base64.b64decode(line.split(', ')[3].encode('utf-8')))
        signature = base64.b64decode(line.split(', ')[-1].encode('utf-8'))

        public_key.verify(
            signature,
            msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verifyLogOrder(self, logs=None):
        if logs == None:
            with open("logs/" + self.filename, 'r') as f:
                lines = [l.strip() for l in f.readlines()]
        else:
            lines = logs

        for i, line in enumerate(lines):
            if i == 0: continue

            prev_line_hashed = base64.b64encode(self.hash(lines[i - 1].encode('utf-8')))
            hash_prev_line = line.split(', ')[2].encode('utf-8')

            if (hash_prev_line != prev_line_hashed):
                return False
        return True

    def hash(self, data):
        h = hashes.Hash(hashes.SHA256())
        h.update(data)
        return h.finalize()