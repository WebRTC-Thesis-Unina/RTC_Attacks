# Scenario 7 and 8: Access Bypass and Information Disclosure
### Description
In this scenario, by inserting specific input values, it is possible to bypass login controls and access the VDO.Ninja platform. Then, using a particular query string, sensitive information (e.g., cookies) can be extracted. 
The access bypass is possible because, in the vulnerable version of Mongoose library, BSON attribute inputs are ignored. The information disclosure occurs because some inputs are not properly sanitized.

### How to reproduce the issue - Scenario Access Bypass
As a first step, the containers are started with:
```bash
docker compose up -d --build
```
Assuming that MongoDB Compass is used as the NoSQL database on the host machine, a firewall rule must be created to allow the container to access the host. On Windows, this can be done with:
```bash
New-NetFirewallRule -DisplayName "MongoDB" -Direction Inbound -Protocol TCP -LocalPort 27017 -Action Allow
```
The MongoDB configuration file (```mongod.cfg```) is then modified to allow communication not only through the loopback address:
```bash
# network interfaces
net:
    port: 27017
    bindIp: 0.0.0.0
```

The web page is accessed through a browser at: ```https://<IP_VM>```.
By entering any username or password, access is granted.

### How to reproduce the issue - Scenario Information Disclosure
After being redirected to: ```https://<IP_VM>:8080```, a new attack can be performed. Using:
```bash
https://<IP_VM>:8080/examples/control.html?room=<img src=x onerror=alert(document.cookie)>
```
the page’s cookies are obtained.
