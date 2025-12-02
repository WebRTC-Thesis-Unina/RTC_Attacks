# Scenario 3: Memory Corruption
### Description
In this scenario, due to a malformed request sent to the server, it crashes because of memory corruption: data is written beyond the dynamically allocated memory. There is no validation of the size of <i>tag</i> and <i>branch</i> in a SIP request. It causes segmentation fault and the termination of Kamailio container.

### How to reproduce the issue
In this scenario, the first step is to start the containers:
```bash
docker compose up -d --build
```
Then, access the <i>sipp101</i> container:
```bash
docker exec -it sipp101 bash
```
The malformed message is sent using:
```bash
sipp -sf /sipp/xml/overflow.xml <IP_VM> -m 1
```
where:
- `-sf /sipp/xml/overflow.xml` indicates the XML file containing the malformed SIP Register request;
- `IP_VM` is the IP address of the VM hosting the containers (Kamailio container);
- `-m 1` specifies that only one message is sent.

The effect of this request is the crash of the Kamailio container.
