#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import requests


TOR_INSTANCES = {
    "US": {"port": 9050, "data_dir": "/root/tor-us", "torrc": "/root/tor-us/torrc-us.conf", "country": "US"},
    "FR": {"port": 9051, "data_dir": "/root/tor-fr", "torrc": "/root/tor-fr/torrc-fr.conf", "country": "FR"},
    "NL": {"port": 9052, "data_dir": "/root/tor-nl", "torrc": "/root/tor-nl/torrc-nl.conf", "country": "NL"}
}

INTERVAL = 60  
TIMES = 0      

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

    
    if not os.path.isfile(inst["torrc"]):
        with open(inst["torrc"], "w") as f:
            f.write(f"SocksPort {inst['port']}\n")
            f.write(f"DataDirectory {inst['data_dir']}\n")
            f.write(f"ExitNodes {{{inst['country']}}}\n")
            f.write("StrictNodes 1\n")

    
    subprocess.run(f"pkill -f 'tor -f {inst['torrc']}'", shell=True)

    

    subprocess.Popen(f"tor -f {inst['torrc']}", shell=True)
    time.sleep(5)  
    print(f"[+] Tor {inst['country']} on port {inst['port']} started, IP: {ma_ip(inst['port'])}")

os.system("clear")
print("[+] Multi-Tor IP Changer Started\n")


interval_input = input(f"[+] Time interval in sec [default={INTERVAL}]: ") or str(INTERVAL)
times_input = input(f"[+] How many times to change IP? 0=infinite: ") or str(TIMES)

try:
    interval = int(interval_input)
    times = int(times_input)

    if times == 0:
        print("[+] Starting infinite IP change. Ctrl+C to stop.")
        while True:
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst)
            time.sleep(interval)
    else:
        for _ in range(times):
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst)
            time.sleep(interval)
except KeyboardInterrupt:
    print("\n[!] Auto-Tor closed by user.")
