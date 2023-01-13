import os 
# PATH = "cc/callers_certs"
# os.chdir(path) 
  
  
  
def read_pem_file(file_path): 
    with open(file_path, 'rb') as f: 
        file_cert = f.read() 
        f.close()
    return file_cert

def compare_certs(cert1, cert2):
    if cert1 == cert2:
        return True
    return False
  

def certs(cert):  
    for file in os.listdir("cc/callers_certs"): 
        if file.endswith(".pem"): 
            file_path = f"cc/callers_certs/{file}"
            file_cert = read_pem_file(file_path) 

            if compare_certs(cert, file_cert):
                return True

    return False
