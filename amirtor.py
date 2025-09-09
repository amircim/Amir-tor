#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import requests

# --- Tor instances configuration ---
TOR_INSTANCES = {
    "US": {"port": 9050, "data_dir": "/var/lib/tor-us", "torrc": "/etc/tor/torrc-us", "country": "US"},
    "FR": {"port": 9051, "data_dir": "/var/lib/tor-fr", "torrc": "/etc/tor/torrc-fr", "country": "FR"},
    "NL": {"port": 9052, "data_dir": "/var/lib/tor-nl", "torrc": "/etc/tor/torrc-nl", "country": "NL"}
}

# --- Helper functions ---
def check_install(pkg):
    try:
        subprocess.check_output(f"which {pkg}", shell=True)
        print(f"[+] {pkg} is installed.")
    except subprocess.CalledProcessError:
        print(f"[!] {pkg} not found, installing...")
        subprocess.check_call(f"sudo apt update && sudo apt install {pkg} -y", shell=True)

def get_tor_bridges():
    """Use the same method as FDX100 Auto-Tor to get bridges."""
    url = "https://bridges.torproject.org/bridges?transport=obfs4"
    try:
        r = requests.get(url, timeout=10)
        # extract obfs4 lines
        lines = [line.strip() for line in r.text.splitlines() if line.startswith("obfs4")]
        return lines if lines else []
    except:
        return []

def write_torrc(instance, bridges):
    os.makedirs(instance["data_dir"], exist_ok=True)
    with open(instance["torrc"], "w") as f:
        f.write(f"SocksPort {instance['port']}\n")
        f.write(f"DataDirectory {instance['data_dir']}\n")
        f.write("UseBridges 1\n")
        f.write("ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy\n")
        for b in bridges:
            f.write(f"{b}\n")

def ma_ip(port):
    url = "http://checkip.amazonaws.com"
    proxies = {"http": f"socks5://127.0.0.1:{port}", "https": f"socks5://127.0.0.1:{port}"}
    try:
        return requests.get(url, proxies=proxies, timeout=10).text.strip()
    except:
        return "Cannot connect"

def start_tor_instance(instance, bridges):
    os.system(f"pkill -f 'tor -f {instance['torrc']}'")
    write_torrc(instance, bridges)
    os.system(f"tor -f {instance['torrc']} &")
    time.sleep(5)
    print(f"[+] Tor {instance['country']} on port {instance['port']} started, IP: {ma_ip(instance['port'])}")

def change_ips(interval=60, loops=0):
    bridges = get_tor_bridges()
    if not bridges:
        print("[!] Could not fetch bridges. Exiting.")
        return

    if loops == 0:
        print("[+] Starting infinite IP change. Ctrl+C to stop.")
        while True:
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst, bridges)
            time.sleep(interval)
    else:
        for _ in range(loops):
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst, bridges)
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
