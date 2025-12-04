# RTP Injection Attack
- Vulnerable component: Asterisk server
- Affected versions: 
    - for class 11.x before 11.25.2
    - for class 13.x before 13.17.1
    - for class 14.x before 14.6.1
- CVE ID: [CVE-2017-14099](https://nvd.nist.gov/vuln/detail/CVE-2017-14099)
## Description
In this scenario, after two clients establish a communication, an attacker can intercept the RTP traffic (due to the RTP Bleed vulnerability) and inject malicious audio into the conversation.

## How to reproduce the issue
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

In the vulnerable versions, if ```nat = yes```, the RTP proxies can automatically learn the attacker's IP and port and send the RTP legitimate traffic to him. After that, the attacker can send a malisous audio and degradeted the connection.

## Mitigations
- Set ```nat = false``` to prevent the proxy from automatically learning information about attackers.
- Use patched version of Asterisk.

## Credits
This vulnerability was discovered by [Enable Security](https://www.enablesecurity.com/)