import socket, string, random, sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cseq = 1
UDP_IP = sys.argv[1]
UDP_PORT = 5060

def build_sip_msg(method, call_id=None, tag=None):
    r = ''.join(random.choice(string.ascii_lowercase) for i in range(10))

    msg = f"{method} sip:{UDP_IP} SIP/2.0\r\n"
    msg += f"Via: SIP/2.0/UDP {UDP_IP}:46786;rport;branch=z9hG4bK-{r}\r\n"
    msg += "Max-Forwards: 70\r\n"
    msg += f"From: <sip:98647499@{UDP_IP}>;tag={tag}\r\n"
    msg += f"To: <sip:98647499@{UDP_IP}>\r\n"
    msg += f"Call-ID: {call_id}\r\n"
    msg += f"CSeq: {cseq} {method}\r\n"
    msg += f"Contact: <sip:98647499@{UDP_IP}:46786;transport=udp>\r\n"

    # Header specifici per ogni metodo
    if method == "REGISTER":
        msg += "Expires: 60\r\n"
        msg += "Content-Length: 0\r\n"
    elif method == "OPTIONS":
        msg += "Content-Length: 0\r\n"
    elif method == "INVITE":
        # body SDP minimo
        sdp = (
            "v=0\r\n"
            f"o=- 0 0 IN IP4 {UDP_IP}\r\n"
            "s=-\r\n"
            f"c=IN IP4 {UDP_IP}\r\n"
            "t=0 0\r\n"
            "m=audio 8000 RTP/AVP 0\r\n"
            "a=rtpmap:0 PCMU/8000\r\n"
        )
        msg += f"Content-Type: application/sdp\r\n"
        msg += f"Content-Length: {len(sdp)}\r\n\r\n"
        msg += sdp
    elif method == "BYE":
        msg += "Content-Length: 0\r\n"
    elif method == "CANCEL":
        msg += "Content-Length: 0\r\n"

    msg += "\r\n"
    return msg

call_id = 'aaaa'
tag = 'tagaaa'

while True:

    for method in ["REGISTER", "OPTIONS", "INVITE", "BYE", "CANCEL"]:
        msg = build_sip_msg(method, call_id=call_id, tag=tag)
        sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
        cseq += 1