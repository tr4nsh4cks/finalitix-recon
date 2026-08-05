#!/bin/bash
VPS="root@212.224.86.211"
PASS="Tr4nsH4ck2026!Ulta"
SSH="sshpass -p $PASS ssh -o StrictHostKeyChecking=accept-new"
$SSH $VPS 'echo "--- uptime:"; uptime; echo "--- os:"; head -2 /etc/os-release; echo "--- apt locks:"; ls -la /var/lib/dpkg/lock-frontend /var/lib/apt/lists/lock 2>/dev/null; fuser /var/lib/dpkg/lock-frontend 2>/dev/null && echo LOCKED || echo NO_LOCK; echo "--- procesos apt/dpkg:"; ps aux | grep -E "apt|dpkg|unattended" | grep -v grep; echo "--- apt update test:"; apt-get update 2>&1 | tail -5'
