#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import subprocess
import requests

TOR_INSTANCES = {
    "US": {"port": 9050, "data_dir": "/root/tor-us", "torrc": "/tmp/torrc-us.conf", "country": "US"},
    "FR": {"port": 9051, "data_dir": "/root/tor-fr", "torrc": "/tmp/torrc-fr.conf", "country": "FR"},
    "NL": {"port": 9052, "data_dir": "/root/tor-nl", "torrc": "/tmp/torrc-nl.conf", "country": "NL"}
}

def ma_ip(port):
    url = "http://checkip.amazonaws.com"
    proxies = {"http": f"socks5://127.0.0.1:{port}", "https": f"socks5://127.0.0.1:{port}"}
    try:
        r = requests.get(url, proxies=proxies, timeout=10)
        return r.text.strip()
    except:
        return "Cannot connect"

def start_tor_instance(inst):
    os.makedirs(inst["data_dir"], exist_ok=True)
    torrc_content = f"""
SocksPort {inst['port']}
DataDirectory {inst['data_dir']}
"""
    with open(inst["torrc"], "w") as f:
        f.write(torrc_content)
    os.system(f"pkill -f 'tor -f {inst['torrc']}'")
    os.system(f"tor -f {inst['torrc']} &")
    time.sleep(5)
    print(f"[+] Tor {inst['country']} on port {inst['port']} started, IP: {ma_ip(inst['port'])}")

os.system("clear")
print("[+] Multi-Tor IP Changer Started\n")
x = input("[+] Time interval in sec [default=60]: ") or "60"
lin = input("[+] How many times to change IP? 0=infinite: ") or "0"

try:
    lin = int(lin)
    interval = int(x)
    if lin == 0:
        print("[+] Starting infinite IP change. Ctrl+C to stop.")
        while True:
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst)
            time.sleep(interval)
    else:
        for _ in range(lin):
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst)
            time.sleep(interval)
except KeyboardInterrupt:
    print("\n[!] Auto-Tor closed by user.")
