# Real-Time Attack Scenarios
The project proposes the implementation of various attack scenarios targeting real-time communication infrastructures.
## Scenario Descriptions
### SIP Spoofing and DoS Attack
In this scenario, SIP Spoofing and DoS attacks (through SIP Flooding) are described. The following components were used:
- <b>FreeSWITCH</b>: container acting as a SIP Server, vulnerable to SIP Spoofing and DoS attacks;
- <b>attacker</b>: alpine container with python installed;
- <b>linphone</b>: special softphone simulating a SIP client.

In this scenario, the first attack consists of sending a SIP Message from an unregistered user impersonating another user (spoofing). In the second attack, continuous registration requests are sent to the FreeSWITCH server, causing the container to crash (DoS via SIP Flooding).

### Memory Corruption
This scenario describes a Memory Corruption attack, caused by a heap overflow vulnerability. The components used are:
- <b>Kamailio</b>: container acting as a SIP Server, vulnerable to heap overflow;
- <b>SIPp</b>: container acting as a SIP Client;
- <b>linphone</b>: special softphone simulating a SIP client.

In this scenario, due to a malformed request sent to the server, it crashes because of Memory Corruption: the data is written beyond the dynamically allocated memory.

### RTP Injection Attack
This scenario describes an RTP Injection attack, caused by an RTP Bleed vulnerability. The following components are used:
- <b>Asterisk</b>: container acting as a SIP Server, vulnerable to RTP Bleed;
- <b>sippts</b>: kali rolling container with sippts installed (a tool for SIP/RTP attacks);
- <b>linphone</b>: special softphone simulating a SIP client.

In this scenario, after two clients establish a communication, an attacker can intercept the RTP traffic (due to the RTP Bleed vulnerability) and inject malicious audio into the conversation.

### Access Bypass
This scenario describes an Access Bypass attack. The components used are:
- <b>coTURN</b>: container emulating a TURN server vulnerable to access bypass attacks;
- <b>STUNner</b>: container acting as a socks5 proxy toward the TURN server.

In this scenario, after creating a socks5 proxy to the TURN server, it is possible using specific HTTP GET requests to access the loopback interface of the server.

### Remote Code Execution
This scenario describes a Ransomware attack caused by a server vulnerability that allows the creation of a webshell through the upload of malicious files. The following component is used:
- <b>node</b>: vulnerable container managing the backend of the web application.

In this scenario, it is possible to upload a malicious javaScript file to execute a webshell on the victim machine. Once this is done, the attacker loads the python ransomware file from their HTTP server and executes it through the webshell. The effect is the encryption of the files on the victim machine.

### Access Bypass and Information Disclosure
This scenario describes two attacks: Access Bypass and Information Disclosure, caused respectively by NoSQLi and XSS vulnerabilities. The following components are used:
- <b>node</b>: container managing the backend of the web application, vulnerable to NoSQLi;
- <b>VDO.Ninja</b>: container simulating the VDO.Ninja platform, used to manage audio-video communication over WebRTC. It is vulnerable to XSS.

In this scenario, by inserting specific input values, it is possible to bypass login controls and access the VDO.Ninja platform. Then, using a particular query string, sensitive information (e.g., cookies) can be extracted.

### Permission abuse
In this scenario, after an initial phase of collecting victim data via phishing, the user is redirected to the attacker's web page. The attacker can, by exploiting a permission abuse, access the user's audio and video streams. The components used are the following:
- <b>node</b>: container managing the backend of the web application;
- <b>GoPhish</b>: container used for conducting phishing campaigns;
- <b>Firefox</b>: container that simulate web browser vulnerable.

In this scenario, after launching the phishing campaign, the user receives the email. They decide to click the button and are redirected to the landing page managed by the attacker. On this page, they enter their data, which is captured by the attacker, and are then redirected to their intended web page. On this page, the user grants permissions to access the microphone and camera. Believing these permissions are used for chat purposes, the user inadvertently allows the attacker to access the audio and video stream, which can then be used on third-party sites.

## Requirements
To use this web application, you need to have the following installed on your local or remote machine:
- Nodejs
- docker
- docker-compose
- git
- make

Additionally, the following applications are required:
- Linphone
- Wireshark
- Firefox

A cloud-based NoSQL database is used:
- MongoDB Atlas

## Database - MongoDB Atlas
Create an account on MongoDB Atlas, then create a cluster and a database. Inside the database, create the following collections:

- ```nosqli_users```
- ```scenarios```

To populate the collections, use the  ```user.json``` and ```scenario.json```files located in the ```database``` folder.

<b>Note:</b> During the cluster creation process, save the ```MONGODB_URI``` connection string and store it in a ```.env``` file using the same variable name.

> <b>Important:</b> To allow the container to access the database, set the allowed IP address to ```0.0.0.0/0```.

<b>Note:</b> Also place a ```.env``` file containing the ```MONGODB_URI``` variable in the folder ```public/labs/7_8_vdo.ninja_xss_nosqli/node_mongoose``` because the server needs access to the MongoDB database.

## SSH Access
To access the local or remote machine, you must use a private key.

If you are accessing the <b>local machine</b>, save your private key (used to authenticate) in a file called ```key_pem.pem```.

If you are accessing the <b>remote machine</b>, follow the instructions in the previous section.

## Setup
After installing the required software and configure the database, clone the repository and move into the project directory:
```bash
git clone https://github.com/WebRTC-Thesis-Unina/RTC_Attacks
cd RTC_Attacks
```
Install the dependencies and start the web application:
```bash
npm install
node server.js
```

After that you can connect at: ```http://localhost:8888```