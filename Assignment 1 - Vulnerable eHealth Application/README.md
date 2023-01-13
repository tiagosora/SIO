# Project 1 - eHealth Corp

<br>

| NMec   | Email                 | Name             
| ------ | --------------------- | ---------------- 
| 102491 | raquelparadinha@ua.pt | Raquel Paradinha 
| 103234 | paulojnpinto02@ua.pt  | Paulo Pinto      
| 103341 | miguelamatos@ua.pt    | Miguel Matos     
| 104142 | tiagogcarvalho@ua.pt  | Tiago Carvalho   

<br>

## Running the project
To run each application, go into their respective folders (either *app* or *app_sec*), and run:
```bash
docker-compose up
```

Both applications will be hosted at http://127.0.0.1:5001, so you can only run one at a time.

For development purposes, we made a script that didn't dockerize the Flask app.  
However, it doesn't work now due to the docker-compose config.
```bash
./devstart.sh
```

<br>

## Exploited Vulnerabilities
* [CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')](https://cwe.mitre.org/data/definitions/79.html) 
* [CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')](https://cwe.mitre.org/data/definitions/89.html) 
* [CWE-522: Insufficiently Protected Credentials](https://cwe.mitre.org/data/definitions/522.html)
* [CWE-521: Weak Password Requirements](https://cwe.mitre.org/data/definitions/521.html)
* [CWE-352: Cross-Site Request Forgery (CSRF)](https://cwe.mitre.org/data/definitions/352.html)
* [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)
* [CWE-200: Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html)
* [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)