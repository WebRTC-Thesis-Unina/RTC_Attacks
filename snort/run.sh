#!/bin/bash
set -euo pipefail

NOW="$(date +'%Y-%m-%d_%H-%M-%S')"
ROOT="captures/${NOW}"
echo "${ROOT}" > captures/last_root.txt

# path iniziali
PCAP_DIR="${ROOT}/pcap"
LOG_DIR="${ROOT}/logs"
META_DIR="${ROOT}/meta"
ANALYSIS_DIR="${ROOT}/analysis"
SNORT_DIR="${ROOT}/snort"
mkdir -p "${PCAP_DIR}" "${LOG_DIR}" "${META_DIR}" "${ANALYSIS_DIR}" "${SNORT_DIR}"

# variabili globali
LAUNCHED_PIDS=()
MONITORED_BRIDGES=()
SNORT_CONTAINER="snort"
SNORT_PID=""
declare -A BRIDGE_TO_PCAP_NAME

# meta info
meta_info(){
    ip -o link > "${META_DIR}/host_links.txt"
    ip -o addr > "${META_DIR}/host_addrs.txt"
}

# Funzione che ricerca i bridge docker esistenti
get_bridges() {
    ip -o link \
        | awk -F': ' '{print $2}' \
        | awk -F':' '{print $1}' \
        | grep '^br-' || true
}

get_lo() {
    ip -o link \
        | awk -F': ' '{print $2}' \
        | awk -F':' '{print $1}' \
        | grep '^lo' || true
}

# Funzione che restituisce il nome della rete a partire dal bridge ID
get_network_name_from_bridge() {
    local bridge_name="$1"
    local network_id="${bridge_name#br-}"
    
    # Cerca la network con questo ID (primi 12 caratteri)
    local network_name=$(docker network ls --format '{{.ID}} {{.Name}}' 2>/dev/null | \
                        grep "^${network_id:0:12}" | \
                        awk '{print $2}' | \
                        head -1)
    
    if [ -n "$network_name" ]; then
        echo "$network_name"
    else
        echo "unknown"
    fi
}

# Crea un nome per il file PCAP
get_pcap_name() {
    local bridge="$1"
    
    # Se già calcolato, usa la cache
    if [ -n "${BRIDGE_TO_PCAP_NAME[$bridge]:-}" ]; then
        echo "${BRIDGE_TO_PCAP_NAME[$bridge]}"
        return
    fi
    
    local network_name=$(get_network_name_from_bridge "$bridge")   
    
    # Rimozione di caratteri problematici
    network_name=$(echo "$network_name" | \
                    tr '/' '_' | \
                    tr ' ' '_' | \
                    tr -cd '[:alnum:]_-')
    
    # Salva in cache
    BRIDGE_TO_PCAP_NAME[$bridge]="$network_name"
    
    echo "$network_name"
}

# Funzione che verifica che un'interfaccia sia UP
is_interface_up() {
    local interface="$1"
    ip link show "$interface" 2>/dev/null | grep -q "state UP"
}

# Funzione che filtra i bridge monitorati restituendo solo quelli ATTIVI
get_active_monitored_bridges() {
    local active=()
    for bridge in "${MONITORED_BRIDGES[@]}"; do
        if is_interface_up "$bridge"; then
            active+=("$bridge")
        fi
    done
    echo "${active[@]}"
}

# Funzione che rimuove i bridge inattivi
cleanup_inactive_bridges() {
    local active_bridges=()
    local removed_count=0
    
    for bridge in "${MONITORED_BRIDGES[@]}"; do
        if is_interface_up "$bridge"; then
            active_bridges+=("$bridge")
        else
            local pcap_name="${BRIDGE_TO_PCAP_NAME[$bridge]:-$bridge}"
            echo "Rimozione bridge inattivo dalla lista: $bridge ($pcap_name)"
            ((removed_count++))
        fi
    done
    
    MONITORED_BRIDGES=("${active_bridges[@]}")
    
    if [ $removed_count -gt 0 ]; then
        echo "✓ Rimossi $removed_count bridge inattivi dalla lista"
        return 0
    fi
    
    return 1
}

# Funzione che raccoglie i log dei container
follow_logs() {
    local name="$1"
    docker logs -f "$name" >> "${LOG_DIR}/${name}.log" 2>&1 &
}

# Funzione che avvia tcpdump sulle interfacce attive
launch_tcpdump(){
    local interface="$1"
    
    if ! is_interface_up "$interface"; then
        echo "WARN: Bridge $interface non è UP, salto tcpdump"
        return 1
    fi
    
    local pcap_name=$(get_pcap_name "$interface")
    local pcap_file="${PCAP_DIR}/${pcap_name}.pcap"
    
    echo "Avvio tcpdump su $interface -> ${pcap_name}.pcap"

    tcpdump -i "$interface" -U -w "$pcap_file" &

    LAUNCHED_PIDS+=($!)
    MONITORED_BRIDGES+=("$interface")
    
    echo "✓ tcpdump avviato: $interface (salvato come ${pcap_name}.pcap)"
}

# Funzione che riavvia snort sulle interfacce attive
restart_snort_container() {
    if [ -n "$SNORT_PID" ] && kill -0 "$SNORT_PID" 2>/dev/null; then
        kill "$SNORT_PID" 2>/dev/null || true
        wait "$SNORT_PID" 2>/dev/null || true
    fi

    local active_interfaces=($(get_active_monitored_bridges))
    
    if [ ${#active_interfaces[@]} -eq 0 ]; then
        echo "Nessuna interfaccia attiva, Snort non avviato"
        return
    fi

    local interface_args=""
    for iface in "${active_interfaces[@]}"; do
        interface_args="-i ${iface}"
    done
    
    sleep 5
        
    snort -c /usr/local/etc/snort/snort.lua \
        -l ${SNORT_DIR} \
        $interface_args \
        -A full \
        -k none &

    SNORT_PID=$!
    LAUNCHED_PIDS+=($SNORT_PID)
    
    echo "✓ Snort avviato con successo"
    
    docker logs -f "$SNORT_CONTAINER" >> "${LOG_DIR}/snort.log" 2>&1 &
}

# Funzione che verifica la presenza di nuovi bridge
check_new_bridges() {
    local new_bridge_detected=false
    local need_snort_restart=false
    
    for bridge in $(get_bridges); do
        if [[ ! " ${MONITORED_BRIDGES[*]} " =~ " ${bridge} " ]]; then
            local retries=0
            while ! is_interface_up "$bridge" && [ $retries -lt 5 ]; do
                sleep 1
                ((retries++))
            done
            
            if is_interface_up "$bridge"; then
                local network_name=$(get_network_name_from_bridge "$bridge")
                echo "Nuovo bridge ATTIVO rilevato: $bridge (network: $network_name)"
                ip link set "$bridge" promisc on
                if launch_tcpdump "$bridge"; then
                    new_bridge_detected=true
                fi
            else
                echo "Bridge $bridge rilevato ma NON attivo, salto"
            fi
        fi
    done
    
    if cleanup_inactive_bridges; then
        need_snort_restart=true
    fi
    
    if [ "$new_bridge_detected" = true ] || [ "$need_snort_restart" = true ]; then
        echo "Stato interfacce cambiato, restart Snort con interfacce attive..."
        restart_snort_container
    fi
}

LOOPBACK_STARTED=false

check_loopback() {
    if [ "$LOOPBACK_STARTED" = true ]; then
        return 0
    fi

    local lo_iface
    lo_iface=$(get_lo | head -1)

    echo "Avvio cattura su loopback ($lo_iface) per container host-network..."

    # Cattura tutto il traffico non puramente localhost
    tcpdump -i "$lo_iface" -U -w "${PCAP_DIR}/loopback.pcap" 'not host 127.0.0.1' &
    LAUNCHED_PIDS+=($!)

    snort -c /usr/local/etc/snort/snort.lua \
        -l "${SNORT_DIR}" \
        -i "$lo_iface" \
        -A full \
        -k none &
    SNORT_PID=$!
    LAUNCHED_PIDS+=($SNORT_PID)

    LOOPBACK_STARTED=true
    echo "✓ Loopback monitoring avviato su $lo_iface"
}

# Funzione richiamata alla terminazione del container snort. Essa si occupa di terminare
# tutti i processi attivi in quel momento
cleanup() {
    echo "=========================================="
    echo "Pulizia in corso..."
    echo "=========================================="
    python3 metrics.py

    sleep 5

    for pid in "${LAUNCHED_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    
    for bridge in "${MONITORED_BRIDGES[@]}"; do
        if ip link show "$bridge" &>/dev/null; then
            ip link set "$bridge" promisc off 2>/dev/null || true
        fi
    done
    
    echo "=========================================="
    echo "Sessione di monitoraggio completata"
    echo ""
    echo "File PCAP generati:"
    if ls "${PCAP_DIR}/"*.pcap &>/dev/null; then
        for pcap in "${PCAP_DIR}/"*.pcap; do
            local size=$(du -h "$pcap" | cut -f1)
            local name=$(basename "$pcap")
            echo "  📦 $name ($size)"
        done
    else
        echo "  Nessun file PCAP generato"
    fi
    echo ""
    echo "Bridge monitorati durante la sessione:"
    for bridge in "${!BRIDGE_TO_PCAP_NAME[@]}"; do
        local status="DOWN"
        if is_interface_up "$bridge"; then
            status="UP"
        fi
        echo "  🌉 $bridge -> ${BRIDGE_TO_PCAP_NAME[$bridge]} [$status]"
    done
    echo "=========================================="

    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "=========================================="
echo "Inizio monitoraggio - $(date)"
echo "Dati salvati in: ${ROOT}"
echo "=========================================="
meta_info

# In caso di container già esistenti raccoglie i log di questi e verifica la presenza 
# di nuovi bridge
echo "Raccolta log container esistenti..."
while read -r id name; do
    follow_logs "$name"
done < <(docker ps --format "{{.ID}} {{.Names}}")

echo ""
echo "Controllo bridge esistenti..."
check_new_bridges

handle_new_container() {
    local container_id="$1"
    local container_name="$2"

    follow_logs "$container_name"

    local net_mode
    net_mode=$(docker inspect --format '{{.HostConfig.NetworkMode}}' "$container_id" 2>/dev/null || echo "")

    if [ "$net_mode" = "host" ]; then
        echo "Container host-network rilevato: $container_name"
        check_loopback
    fi
}

# In caso di avvio di nuovi container (event = start), si ricavano i suoi log
while read -r container_id container_name; do
    handle_new_container "$container_id" "$container_name"
done < <(
    docker events \
        --filter 'type=container' \
        --filter 'event=start' \
        --format '{{.ID}} {{.Actor.Attributes.name}}'
) &

# In caso di evento = connect, si ricavano le metà info e si verifica la presenza di 
# nuovi bridge
while read -r network_id container_id; do
    sleep 2
    meta_info
    check_new_bridges
done < <(
    docker events \
        --filter 'type=network' \
        --filter 'event=connect' \
        --format '{{.ID}} {{.Actor.Attributes.container}}'
) &

wait