#!/bin/sh

error() {
    MSG="$1"
    echo "[ERROR] $MSG"
}

usage() {
    echo "Usage: $0 <N> [VBOX-HOST-ONLY-IF]"
    echo
    echo "positional arguments:"
    echo "  N  (required) The number of wanted IP addresses."
    echo "  VBOX-HOST-ONLY-IF  (optional) The information about the VirtualBox"
    echo "     host-only network interface (IPAddress, NetworkMask). If not"
    echo "     provided, will be read from stdin."
}

# test $# -eq 2 || {
#     usage
#     exit 2
# }

N=$1

# sleep 1

exit 0

# Create the temporary storage.
TMP_DIR=$(mktemp --directory) || exit 2

cleanup() {
    rm -fr "$TMP_DIR" || echo "WARNING: cleanup() failed to remove \"$TMP_DIR\"" >&2
}
trap cleanup EXIT INT TERM

VBOX_HOST_ONLY_IF=

if [ -z ${2+x} ];
then
    VBOX_HOST_ONLY_IF="$TMP_DIR/vbox_host_only_if.txt"
    cat < /dev/stdin > "$VBOX_HOST_ONLY_IF"
else
    VBOX_HOST_ONLY_IF="$2"
fi

VBOX_IF_IPADDR=$(jq --raw-output ".IPAddress" < "${VBOX_HOST_ONLY_IF}") || exit 2
VBOX_IF_NETMASK=$(jq --raw-output ".NetworkMask" < "${VBOX_HOST_ONLY_IF}") || exit 2

ipcalc "${VBOX_IF_IPADDR}/${VBOX_IF_NETMASK}" > "$TMP_DIR/ipcalc" || exit 2

grep "HostMin" "$TMP_DIR/ipcalc" > "$TMP_DIR/host_min_line" || exit 2
grep "HostMax" "$TMP_DIR/ipcalc" > "$TMP_DIR/host_max_line" || exit 2

IPV4_REGEX="[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" # escaped
HOST_MIN_IP=$(grep -o "$IPV4_REGEX" "$TMP_DIR/host_min_line") || exit 2
HOST_MAX_IP=$(grep -o "$IPV4_REGEX" "$TMP_DIR/host_max_line") || exit 2

# Need the utility `prips`.
prips "$HOST_MIN_IP" "$HOST_MAX_IP" > "$TMP_DIR/ip_candidates" || exit 2

# Shuffle the IPs.
shuf "$TMP_DIR/ip_candidates" > "$TMP_DIR/shuffled_ips" || exit 2

COUNT=$(wc -l < "$TMP_DIR/shuffled_ips") || exit 2

# Make sure we have enough candidates to choose from.
test $N -le $COUNT || {
    error "The wanted number of IPs ($N) is greater than the available number ($COUNT)."
    exit 2
}

# Just use the first N IPs.
head -n $N < "$TMP_DIR/shuffled_ips" || exit 2
