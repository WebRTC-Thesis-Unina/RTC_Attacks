# Access Bypass and Information Disclosure
- Vulnerable components: mongoose library, VDO.Ninja
- Affected versions:
    - for mongoose: ≤ 5.7.4
    - for VDO.Ninja: 28.0
- CVE IDs: [CVE-2019-17426](https://nvd.nist.gov/vuln/detail/CVE-2019-17426), [CVE-2025-62613](https://nvd.nist.gov/vuln/detail/CVE-2025-62613)

## Description
In this scenario, by inserting specific input values, it is possible to bypass login controls and access the VDO.Ninja platform. Then, using a particular query string, sensitive information (e.g., cookies) can be extracted.

## How to reproduce the issue - Access Bypass
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

The web page is accessed through a browser at: ```https://<IP_VM>```. In the vulnerable versions, the ```_bsontype``` attribute is ignored by server, and therefore by entering any username or password, access is granted.

## Mitigations
- Update to patched versions.
- Improve server-side validation controls.

## How to reproduce the issue - Information Disclosure
After being redirected to: ```https://<IP_VM>:8080```, a new attack can be performed. Using:
```bash
https://<IP_VM>:8080/examples/control.html?room=<img src=x onerror=alert(document.cookie)>
```
the page’s cookies are obtained.

For the vulnerable versions, there is no sanification of this particular input.

## Mitigation
- Update to patched version.