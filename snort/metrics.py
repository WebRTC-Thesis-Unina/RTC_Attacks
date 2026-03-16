import pandas as pd
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = ""

# Funzione che converte pcap in csv, estraendo le metriche principali
def pcap_to_csv(input_file, output_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "tshark", "-r", str(input_file),
        "-Y", "ip || icmp || udp || sip || http || stun", "-T", "fields", 
        "-E", "header=y", "-E", "separator=,", "-E", "quote=d",
        "-e", "frame.time", "-e", "ip.src", "-e", "udp.srcport",
        "-e", "ip.dst", "-e", "udp.dstport", "-e", "ip.ttl",
        "-e", "ip.version", "-e", "ip.hdr_len", "-e", "ip.len",
        "-e", "udp.length", "-e", "ip.checksum", "-e", "udp.checksum",
        "-e", "icmp.type", "-e", "icmp.code", "-e", "icmp.checksum",
        "-e", "icmp.seq", "-e", "rtp.ssrc", "-e", "rtp.seq",
        "-e", "rtp.timestamp", "-e", "sip.Method", "-e", "sip.Call-ID",
        "-e", "sip.From", "-e", "sip.from.tag", "-e", "sip.To",
        "-e", "sip.CSeq", "-e", "tcp.srcport", "-e", "tcp.dstport",
        "-e", "http.request.method", "-e", "http.request.full_uri",
        "-e", "http.request.uri.query", "-e", "http.response.code",
        "-e", "http.user_agent", "-e", "stun.att.ipv4", "-e", "stun.att.ipv6"
    ]

    with open(output_file, "w") as f:
        subprocess.run(cmd, stdout=f, check=True)
    
# Preprocessing dei dati
def preprocessing(input_file, output_file):
    df = pd.read_csv(input_file, low_memory=False)

    numeric_cols = [
        "udp.srcport", "udp.dstport", "ip.ttl",
        "ip.version", "ip.hdr_len", "ip.len",
        "udp.length", "ip.checksum", "udp.checksum",
        "icmp.type", "icmp.code", "icmp.checksum",
        "icmp.seq", "rtp.seq", "rtp.timestamp",
        "sip.CSeq", "tcp.srcport", "tcp.dstport",
        "http.response.code",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    if "frame.time" in df.columns:
        df["frame.time"] = pd.to_datetime(
            df["frame.time"].str.strip(),
            format="%b %d, %Y %H:%M:%S.%f %Z",
            utc=True
        ).dt.strftime("%m/%d-%H:%M:%S.%f")

    df.to_csv(output_file, index=False)

# Funzione che ricava dal file di log il timestamp, ricerca flussi che hanno 
# comportamento anomalo e li etichetta come malevoli con la label specifica
def check_attacks(input_file, snort_file, output_file):
    df = pd.read_csv(input_file, low_memory=False)
    timestamps = set()
    df["attack"] = "none"

    with open(snort_file, "r") as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if line.startswith("[**]"):
            ts_index = i + 2
            if ts_index < len(lines):
                ts_line = lines[ts_index].strip()
                ts = ts_line.split(" ")[0]
                timestamps.add(ts)
    
    if not timestamps:
        return
    
    # Se esiste almeno un alert tra i log classifica il traffico
    mask = df["frame.time"].astype(str).isin(timestamps)

    # SIP Spoofing: messaggio proveniente da UniCredit
    df.loc[mask & df["sip.From"].fillna("").astype(str).str.contains("UniCredit"), "attack"] = "sip_spoofing"

    # SIP Register Flood: più di 100 REGISTER dallo stesso IP
    register_counts = (
        df[df["sip.Method"].fillna("").astype(str) == "REGISTER"]
        .groupby("ip.src")
        .size()
    )

    flood_ips = register_counts[register_counts > 100].index

    df.loc[
        mask & 
        (df["ip.src"].isin(flood_ips)) & 
        (df["sip.Method"].fillna("").astype(str) == "REGISTER"),
        "attack"
    ] = "sip_register_flood"

    # SIP Overflow: lunghezza del campo tag di From superiore a 20
    df.loc[mask & (df["sip.from.tag"].fillna("").astype(str).str.len() > 20), "attack"] = "sip_overflow"
    
    # RTP Injection Flood: se esistono più di 100 richieste dallo stesso IP per il range 
    # di porte riportate, si segnala la presenza di attacco
    rtp_counts = (
        df[df["udp.dstport"].between(10000, 10099)]
        .groupby("ip.src")
        .size()
    )

    flood_ips = rtp_counts[rtp_counts > 100].index

    df.loc[
        mask & 
        df["ip.src"].isin(flood_ips) &
        df["udp.dstport"].between(10000, 10099),
        "attack"
    ] = "rtp_injection"

    # Conversione timestamp in float
    alert_times = pd.to_datetime(list(timestamps), format="%m/%d-%H:%M:%S.%f", utc=True)

    # Conversione frame.time in datetime per confronto
    frame_times = pd.to_datetime(df["frame.time"], format="%m/%d-%H:%M:%S.%f", utc=True)

    # time_mask: vero se il pacchetto è entro ±5µs
    epsilon = pd.Timedelta(microseconds=5)
    time_mask = frame_times.apply(
        lambda t: any(abs(t - at) <= epsilon for at in alert_times)
    )

    # Coturn Access Bypass: tutto il traffico generato verso il server Coturn con IP "::"
    # o "::1" è etichettato come malevolo (si classifica tutto il traffico proveniente 
    # dallo specifico IP) in questo modo anche il traffico successivo è classificato 
    # come malevolo
    turn_mask = (
        time_mask &
        ((df["tcp.dstport"] == 3478) |
        (df["udp.dstport"] == 3478))
    )

    loopback_mask = df["stun.att.ipv6"].fillna("").astype(str).str.contains(r"::1|::")
    attack_trigger = turn_mask & loopback_mask
    attacker_ips = df.loc[attack_trigger, "ip.src"].unique()

    df.loc[
        df["ip.src"].isin(attacker_ips) |
        df["ip.dst"].isin(attacker_ips),
        "attack"
    ] = "coturn_access_bypass"

    # RCE: se nella richiesta HTTP l'utente inserisce "cmd=", questo è un segnale di RCE
    attack_trigger = (
        mask & 
        (
            df["http.request.full_uri"].fillna("").astype(str).str.contains("cmd=") |
            df["http.request.uri.query"].fillna("").astype(str).str.contains("cmd=")
        )
    )

    df.loc[
        attack_trigger,
        "attack"
    ] = "remote_code_execution"

    # XSS: in caso di inserimento dei seguenti caratteri ci si trova d'innanzi a XSS
    attack_trigger = (
        time_mask &
        (
            df["http.request.full_uri"].fillna("").astype(str).str.contains("alert") |
            df["http.request.full_uri"].fillna("").astype(str).str.contains("script") |
            df["http.request.full_uri"].fillna("").astype(str).str.contains("onerror") |
            df["http.request.full_uri"].fillna("").astype(str).str.contains("document.cookie")
        )
    )

    df.loc[
        attack_trigger,
        "attack"
    ] = "cross_side_scripting"

    # Permission Abuse: l'user agent vulnerabile è Firefox 68
    df.loc[
        mask & 
        (df["http.user_agent"].fillna("").astype(str).str.contains("Firefox/68.0")),
        "attack"
    ] = "permission_abuse"

    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    with open("./captures/last_root.txt", mode="r") as f:
        ROOT = Path(f.readline().strip().replace("\r", ""))
    
    pcap_dir = ROOT / "pcap"
    analysis_dir = ROOT / "analysis"
    snort_dir = ROOT / "snort"

    for pcap in pcap_dir.glob("*.pcap"):
        out_csv = analysis_dir / f"{pcap.stem}.csv"
        pcap_to_csv(pcap, out_csv)

    for csv in analysis_dir.glob("*.csv"):
        preprocessing(
            input_file=analysis_dir / f"{csv.stem}.csv", 
            output_file=analysis_dir / f"{csv.stem}.csv",
        )

        check_attacks(
            input_file = analysis_dir / f"{csv.stem}.csv",
            snort_file = snort_dir / "alert_full.txt",
            output_file= analysis_dir / f"{csv.stem}.csv",
        )