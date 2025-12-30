import csv
from collections import defaultdict
import sys

def sip_flood(ROOT):
    REGISTER_THRESHOLD = 20  # Threshold to consider SIP flood

    SIP_CSV = ROOT + "/metrics/sip.csv"

    ip_counts = defaultdict(int)

    with open(SIP_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        
        for row in reader:
            if row["sip.Method"] != "REGISTER":
                continue

            dst_ips = row["ip.dst"].split(",")
            for dst_ip in dst_ips:
                dst_ip = dst_ip.strip()
                ip_counts[dst_ip] += 1

    with open("alert.log", mode="w") as f:
        for dst_ip, count in ip_counts.items():
            if count >= REGISTER_THRESHOLD:
                f.write(f"[ALERT] SIP FLOOD detected for dst_ip={dst_ip} (messages={count})\n")
    
def heap_overflow(ROOT):
    SIP_CSV = ROOT + "/metrics/sip.csv"
    LEN_THRESHOLD = 20
    
    seen_tags = set() # already processed

    with open(SIP_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')

        for row in reader:
            method = row["sip.Method"]
            if method != "REGISTER":
                continue

            tag = row["sip.tag"]

            if tag in seen_tags:
                    continue

            seen_tags.add(tag)

    for t in seen_tags:
        with open("alert.log", mode="a") as f:
            if len(t) >= LEN_THRESHOLD:
                f.write(f"[ALERT] HEAP OVERFLOW detected (tag={t})\n")

def rtp_injection(ROOT):
    RTP_CSV = ROOT + "/metrics/rtp.csv"

    streams = {}  # (src_ip, dst_ip, src_port, dst_port)

    seen_stream = set() # already processed

    with open(RTP_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            key = (
                row["ip.src"],
                row["ip.dst"],
                row["udp.srcport"],
                row["udp.dstport"]
            )

            ssrc = row["rtp.ssrc"]

            if key not in streams:
                streams[key] = ssrc
                continue

            stream = streams[key]

            if stream in seen_stream:
                continue

            seen_stream.add(stream)

            for s in seen_stream:
                with open("alert.log", "a") as f:
                    if ssrc != s:
                        f.write(f"[ALERT] RTP INJECTION detected: SSRC expected={s} - SSRC received={ssrc}\n")

def access_bypass(ROOT):
    STUN_CSV = ROOT + "/metrics/stun.csv"
    xor_peer_ipv4 = ""
    xor_peer_ipv6 = ""

    with open(STUN_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')

        for row in reader:
            if not (
                row["stun.att.ipv4"] == "0.0.0.0" or
                row["stun.att.ipv6"] == "::1" or
                row["stun.att.ipv6"] == "::"
            ):
                continue

            xor_peer_ipv4 = row["stun.att.ipv4"]
            xor_peer_ipv6 = row["stun.att.ipv6"]

            if not (
                row["ip.src"] == "10.0.0.4" and row["ip.dst"] == "10.0.0.10"
            ):
                continue


            with open("alert.log", mode="a") as f:
                if xor_peer_ipv4:
                    f.write(f"[ALERT] ACCESS BYPASS using XOR-PEER-ADDRESS ipv4={xor_peer_ipv4}\n")
                elif xor_peer_ipv6:
                    f.write(f"[ALERT] ACCESS BYPASS using XOR-PEER-ADDRESS ipv6={xor_peer_ipv6}\n")

def webshell(ROOT):
    HTTP_CSV = ROOT + "/metrics/http.csv"
    count = 0
    with open(HTTP_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')

        for row in reader:
            if not (
                (row["http.request.uri.query"]).startswith("cmd=")
            ):
                continue
            count += 1

    with open("alert.log", mode="a") as f:
        if count >= 1:
            f.write("[ALERT] REMOTE CODE EXECUTION detected - Webshell file was uploaded")

if __name__ == "__main__":
    ROOT = ""
    with open("./captures/last_root.txt", mode="r") as f:
        ROOT = "." + f.readline().strip()
    sip_flood(ROOT)
    heap_overflow(ROOT)
    rtp_injection(ROOT)
    access_bypass(ROOT)
    webshell(ROOT)