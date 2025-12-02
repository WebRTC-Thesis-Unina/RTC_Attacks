# Scenario 4: RTP Injection Attack
### Description
In this scenario, after two clients establish a communication, an attacker can intercept the RTP traffic (due to the RTP Bleed vulnerability) and inject malicious audio into the conversation. This is possible because, due to NATting, because the RTP proxies learn the attacker's IP address and subsequently send the RTP stream to him. In this way, it can listen to the legitimate conversation and inject  malignous audio into it.

### How to reproduce the issue
As a first step, the containers are started with:
```bash
docker compose up -d --build
```
For this scenario, the Linphone application must be used to simulate the SIP clients.
Users <b>7001</b> e <b>7002</b> are registered. Below is the registration of user 7001 (the registration procedure for 7002 is analogous):

![registration](/4_rtp_bleed_injection_asterisk/img/7001_registration.png)

The Wireshark container is started to observe the port used for RTP traffic (in the example, RTP uses ports between 10000 and 10099). The following command is used:
```bash
docker exec -it wireshark wireshark
```
The network interface is selected, and a call is initiated between Linphone 7001 and 7002.

Access the <i>sippts</i> container:
```bash
docker exec -it sippts bash
```
and run the script:
```bash
sippts rtpbleedinject -i <IP_VM> -r <port_number> -f audio.wav
```
where:
- ```rtpbleedinject``` indicates the type of attack, namely RTP Injection;
- ```-i <IP_VM>``` represents the IP address of the VM running the Asterisk server;
-```-r <port_number>``` represents the IP address of the VM running the Asterisk server;
- ```-f audio.wav``` indicates the audio file injected into the conversation.

The resulting effect is a degradation of the communication.
