#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import requests

TOR_INSTANCES = {
    "US": {"port": 9050, "data_dir": "/var/lib/tor-us", "torrc": "/etc/tor/torrc-us"},
    "FR": {"port": 9051, "data_dir": "/var/lib/tor-fr", "torrc": "/etc/tor/torrc-fr"},
    "NL": {"port": 9052, "data_dir": "/var/lib/tor-nl", "torrc": "/etc/tor/torrc-nl"}
}

# پل‌های internal برای هر کشور (مثل FDX100)
INTERNAL_BRIDGES = {
    "US": ["obfs4 127.0.0.1:9001 ... iat-mode=0"],
    "FR": ["obfs4 127.0.0.1:9002 ... iat-mode=0"],
    "NL": ["obfs4 127.0.0.1:9003 ... iat-mode=0"]
}

def check_install():
    if not shutil.which("tor"):
        print("[+] Tor not found, installing...")
        os.system("sudo apt update && sudo apt install tor -y")
    if not shutil.which("obfs4proxy"):
        print("[+] obfs4proxy not found, installing...")
        os.system("sudo apt install obfs4proxy -y")

def write_torrc(instance, country):
    os.makedirs(instance["data_dir"], exist_ok=True)
    with open(instance["torrc"], "w") as f:
        f.write(f"SocksPort {instance['port']}\n")
        f.write(f"DataDirectory {instance['data_dir']}\n")
        f.write("UseBridges 1\n")
        f.write("ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy\n")
        for b in INTERNAL_BRIDGES[country]:
            f.write(f"{b}\n")

def get_ip(port):
    proxies = {"http": f"socks5://127.0.0.1:{port}", "https": f"socks5://127.0.0.1:{port}"}
    try:
        return requests.get("http://checkip.amazonaws.com", proxies=proxies, timeout=10).text.strip()
    except:
        return "Cannot connect"

def start_instance(instance, country):
    os.system(f"pkill -f 'tor -f {instance['torrc']}'")
    write_torrc(instance, country)
    os.system(f"tor -f {instance['torrc']} &")
    time.sleep(5)
    print(f"[+] Tor {country} on port {instance['port']} started, IP: {get_ip(instance['port'])}")

def change_ips(interval=60, loops=0):
    if loops == 0:
        print("[+] Starting infinite IP change. Ctrl+C to stop.")
        while True:
            for country, inst in TOR_INSTANCES.items():
                start_instance(inst, country)
            time.sleep(interval)
    else:
        for _ in range(loops):
            for country, inst in TOR_INSTANCES.items():
                start_instance(inst, country)
            time.sleep(interval)

if __name__ == "__main__":
    import shutil
    check_install()
    os.system("clear")
    print("[+] Multi-Tor IP Changer (FDX100 style) Started")
    interval = input("[+] Time interval in sec [default=60]: ") or "60"
    loops = input("[+] How many times to change IP? 0=infinite: ") or "0"
    try:
        change_ips(interval=int(interval), loops=int(loops))
    except KeyboardInterrupt:
        print("\n[!] Auto-Tor closed by user.")
