#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import subprocess
import requests

# سه instance Tor
TOR_INSTANCES = {
    "US": {"port": 9050, "data_dir": "/var/lib/tor-us", "torrc": "/etc/tor/torrc-us", "country": "US"},
    "FR": {"port": 9051, "data_dir": "/var/lib/tor-fr", "torrc": "/etc/tor/torrc-fr", "country": "FR"},
    "NL": {"port": 9052, "data_dir": "/var/lib/tor-nl", "torrc": "/etc/tor/torrc-nl", "country": "NL"}
}

def get_bridges(country):
    """
    تابع نمونه برای گرفتن پل‌های تازه از Tor Project یا ربات خودکار
    اینجا می‌توانی API پل‌ها یا لیست خودکار bridges اضافه کنی
    """
    # نمونه دستی برای تست (می‌توان اتوماتیک گرفت)
    bridges = {
        "US": ["obfs4 185.220.101.1:443 ... iat-mode=0"],
        "FR": ["obfs4 81.6.45.148:9143 ... iat-mode=0"],
        "NL": ["obfs4 2a02:168:673b::1:9143 ... iat-mode=0"]
    }
    return bridges.get(country, [])

def write_torrc(instance):
    bridges = get_bridges(instance["country"])
    os.makedirs(instance["data_dir"], exist_ok=True)
    with open(instance["torrc"], "w") as f:
        f.write(f"SocksPort {instance['port']}\n")
        f.write(f"DataDirectory {instance['data_dir']}\n")
        f.write("UseBridges 1\n")
        f.write("ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy\n")
        for b in bridges:
            f.write(f"{b}\n")

def ma_ip(port):
    url = 'http://checkip.amazonaws.com'
    proxies = dict(http=f'socks5://127.0.0.1:{port}', https=f'socks5://127.0.0.1:{port}')
    try:
        r = requests.get(url, proxies=proxies, timeout=10)
        return r.text.strip()
    except:
        return "Cannot connect"

def start_tor_instance(instance):
    # Kill هر Tor قدیمی روی پورت
    os.system(f"pkill -f 'tor -f {instance['torrc']}'")
    # نوشتن torrc
    write_torrc(instance)
    # اجرای Tor instance
    os.system(f"tor -f {instance['torrc']} &")
    time.sleep(5)
    print(f"[+] Tor {instance['country']} on port {instance['port']} started, IP: {ma_ip(instance['port'])}")

def change_ips(interval=60, loops=0):
    if loops == 0:
        print("[+] Starting infinite IP change. Ctrl+C to stop.")
        while True:
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst)
            time.sleep(interval)
    else:
        for _ in range(loops):
            for _, inst in TOR_INSTANCES.items():
                start_tor_instance(inst)
            time.sleep(interval)

# Main
os.system("clear")
print("[+] Multi-Tor IP Changer Started\n")
x = input("[+] Time interval in sec [default=60]: ") or "60"
lin = input("[+] How many times to change IP? 0=infinite: ") or "0"

try:
    change_ips(interval=int(x), loops=int(lin))
except KeyboardInterrupt:
    print("\n[!] Auto-Tor closed by user.")
