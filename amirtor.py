sudo bash -c 'cat > /root/amirtor_auto.py << "EOF"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import requests

# --- Configuration ---
TOR_INSTANCES = {
    "US": {"port": 9050, "data_dir": "/var/lib/tor-us", "torrc": "/etc/tor/torrc-us", "country": "US"},
    "FR": {"port": 9051, "data_dir": "/var/lib/tor-fr", "torrc": "/etc/tor/torrc-fr", "country": "FR"},
    "NL": {"port": 9052, "data_dir": "/var/lib/tor-nl", "torrc": "/etc/tor/torrc-nl", "country": "NL"}
}

BRIDGES = {
    "US": ["obfs4 185.220.101.1:443 ... iat-mode=0"],
    "FR": ["obfs4 81.6.45.148:9143 ... iat-mode=0"],
    "NL": ["obfs4 2a02:168:673b::1:9143 ... iat-mode=0"]
}

# --- Helper functions ---
def check_install(pkg):
    try:
        subprocess.check_output(f"which {pkg}", shell=True)
        print(f'[+] {pkg} is installed.')
        return True
    except subprocess.CalledProcessError:
        print(f'[!] {pkg} not found, installing...')
        subprocess.check_call(f"sudo apt update && sudo apt install {pkg} -y", shell=True)
        return True

def write_torrc(instance):
    os.makedirs(instance["data_dir"], exist_ok=True)
    with open(instance["torrc"], "w") as f:
        f.write(f"SocksPort {instance['port']}\n")
        f.write(f"DataDirectory {instance['data_dir']}\n")
        f.write("UseBridges 1\n")
        f.write("ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy\n")
        for b in BRIDGES[instance["country"]]:
            f.write(f"{b}\n")

def ma_ip(port):
    url = "http://checkip.amazonaws.com"
    proxies = {"http": f"socks5://127.0.0.1:{port}", "https": f"socks5://127.0.0.1:{port}"}
    try:
        return requests.get(url, proxies=proxies, timeout=10).text.strip()
    except:
        return "Cannot connect"

def start_tor(instance):
    os.system(f"pkill -f 'tor -f {instance['torrc']}'")
    write_torrc(instance)
    os.system(f"tor -f {instance['torrc']} &")
    time.sleep(5)
    print(f"[+] Tor {instance['country']} on port {instance['port']} started, IP: {ma_ip(instance['port'])}")

def change_ips(interval=60, loops=0):
    if loops == 0:
        print("[+] Starting infinite IP change. Ctrl+C to stop.")
        while True:
            for _, inst in TOR_INSTANCES.items():
                start_tor(inst)
            time.sleep(interval)
    else:
        for _ in range(loops):
            for _, inst in TOR_INSTANCES.items():
                start_tor(inst)
            time.sleep(interval)

# --- Main ---
os.system("clear")
check_install("tor")
check_install("obfs4proxy")

x = input("[+] Time interval in sec [default=60]: ") or "60"
lin = input("[+] How many times to change IP? 0=infinite: ") or "0"

try:
    change_ips(interval=int(x), loops=int(lin))
except KeyboardInterrupt:
    print("\n[!] Auto-Tor closed by user.")
EOF
