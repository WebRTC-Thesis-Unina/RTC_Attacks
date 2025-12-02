# Scenario 1 and 2: SIP Spoofing and DoS Attack
### Description
In this scenario, the first attack consists of sending a SIP Message from an unregistered user impersonating another user (spoofing). This is possible because everyone can send a SIP MESSAGE without authentication. In the second attack, continuous registration requests are sent to the FreeSWITCH server, causing the container to crash (DoS via SIP Flooding). There's no mechanism to rate-limit these requests. The server keeps allocating memory, and after many requests the memory limit is reached, causing the container to terminate.

### How to reproduce the issue - Scenario SIP Spoofing
For both attacks, the Linphone application is used. For the first scenario, a user must be registered. FreeSWITCH provides default users ranging from <b>1000</b> to <b>1020</b> (it is recommended to use one of these).
The username corresponds to the chosen value, while the password is <b>1234</b>.
To complete the registration, the SIP server must be specified. The IP address of the VM hosting the containers is used:

![registration](/1_2_sip_spoofing_dos_freeswitch/img/1001.png)

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
- `clientSIP` is the number of the SIP client (linphone);

As a result, the following message will appear:
![spoofing](/1_2_sip_spoofing_dos_freeswitch/img/message_unicredit.png)

### How to reproduce the issue - Scenario DoS via SIP Flood
In the second scenario, again from the attacker container, the following is executed:
```bash
python3 spoofing.py <IP_VM>
```
The effect can be observed by monitoring the container statistics using `docker stats`. The memory limit is reached first, after which the container eventually terminates.
