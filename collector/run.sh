#!/usr/bin/env bash
set -euo pipefail

# --- init paths ---
NOW="$(date +'%Y-%m-%d_%H-%M-%S')"
ROOT="/captures/${NOW}"
echo "${ROOT}" > /captures/last_root.txt

PCAP_DIR="${ROOT}/pcap"
LOG_DIR="${ROOT}/logs"
META_DIR="${ROOT}/meta"
METRICS_DIR="${ROOT}/metrics"
mkdir -p "${PCAP_DIR}" "${LOG_DIR}" "${META_DIR}" "${METRICS_DIR}"

# --- meta info ---
ip -o link > "${META_DIR}/host_links.txt"
ip -o addr > "${META_DIR}/host_addrs.txt"

TCPDUMP_PID=""
cleanup() {
    if [[ -n "${TCPDUMP_PID}" ]] && kill -0 "${TCPDUMP_PID}" 2>/dev/null; then
        kill -TERM "${TCPDUMP_PID}"
        wait "${TCPDUMP_PID}" || true
    fi
}

trap cleanup SIGTERM SIGINT

# --- logs ---
for elem in $(docker ps -a --format '{{.Names}}'); do
    docker logs "$elem" >> "${LOG_DIR}/${elem}.log"
done

# --- pcap captures ---
tcpdump -i any -w "${PCAP_DIR}/flow.pcap" &
TCPDUMP_PID=$!
wait "${TCPDUMP_PID}" || true

# --- csv creations ---
tshark -r "${PCAP_DIR}/flow.pcap" -Y "udp" -T fields \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst \
  -e udp.srcport \
  -e udp.dstport \
  -e frame.len \
  -E header=y \
  -E separator=, \
  -E quote=d \
  > "${METRICS_DIR}/udp.csv" &

tshark -r "${PCAP_DIR}/flow.pcap" -Y "tcp" -T fields \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst \
  -e tcp.srcport \
  -e tcp.dstport \
  -e tcp.seq_raw \
  -e tcp.ack_raw \
  -e tcp.flags \
  -e tcp.window_size_value \
  -e tcp.len \
  -e frame.len \
  -E header=y \
  -E separator=, \
  -E quote=d \
  > "${METRICS_DIR}/tcp.csv" &

tshark -r "${PCAP_DIR}/flow.pcap" -Y "sip" -T fields \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst \
  -e udp.srcport \
  -e udp.dstport \
  -e sip.Method \
  -e sip.tag \
  -e sip.Status-Code \
  -e sip.Call-ID \
  -E header=y \
  -E separator=, \
  -E quote=d \
  > "${METRICS_DIR}/sip.csv" &

tshark -r "${PCAP_DIR}/flow.pcap" -Y "rtp" -T fields \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst \
  -e udp.srcport \
  -e udp.dstport \
  -e rtp.ssrc \
  -e rtp.seq \
  -e rtp.timestamp \
  -e rtp.payload \
  -e frame.len \
  -E header=y \
  -E separator=, \
  -E quote=d \
  > "${METRICS_DIR}/rtp.csv" &

tshark -r "${PCAP_DIR}/flow.pcap" -Y "stun" -T fields \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst \
  -e stun.att.ipv4 \
  -e stun.att.ipv6 \
  -e frame.len \
  -E header=y \
  -E separator=, \
  -E quote=d \
  > "${METRICS_DIR}/stun.csv" &

tshark -r "${PCAP_DIR}/flow.pcap" -Y "http" -T fields \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst \
  -e http.request.method \
  -e http.request.uri.query \
  -E header=y \
  -E separator=, \
  -E quote=d \
  > "${METRICS_DIR}/http.csv"