# -*- coding: utf-8 -*-

import time
import os
import subprocess
import requests

TOR_INSTANCES = {
    "US": 9050,
    "FR": 9051,
    "NL": 9052
}

def install_requirements():
    try:
        import requests
    except:
        os.system("pip3 install requests requests[socks]")

    try:
        subprocess.check_output("which tor", shell=True)
    except subprocess.CalledProcessError:
        os.system("sudo apt update && sudo apt install tor -y")

def ma_ip(port):
    url = "http://checkip.amazonaws.com"
    try:
        r = requests.get(url, proxies={"http": f"socks5://127.0.0.1:{port}", "https": f"socks5://127.0.0.1:{port}"}, timeout=10)
        return r.text.strip()
    except:
        return "Cannot connect"

def start_tor(port, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    torrc = f"/tmp/torrc-{port}.conf"
    with open(torrc, "w") as f:
        f.write(f"SocksPort {port}\n")
        f.write(f"DataDirectory {data_dir}\n")
    # Kill any existing tor on this port
    os.system(f"pkill -f 'tor -f {torrc}'")
    # Start tor instance
    os.system(f"tor -f {torrc} &")
    time.sleep(5)

def change_all_ips():
    for country, port in TOR_INSTANCES.items():
        start_tor(port, f"/var/lib/tor-{country.lower()}")
        print(f"[+] Tor {country} on port {port} started, IP: {ma_ip(port)}")

if __name__ == "__main__":
    install_requirements()
    os.system("clear")
    print("[+] Multi-Tor IP Changer Started\n")
    interval = input("[+] Time interval in sec [default=60]: ") or "60"
    loops = input("[+] How many times do you want to change your IP? 0=infinite >> ") or "0"

    try:
        interval = int(interval)
        loops = int(loops)
        if loops == 0:
            print("[+] Starting infinite IP change. Ctrl+C to stop.")
            while True:
                change_all_ips()
                time.sleep(interval)
        else:
            for _ in range(loops):
                change_all_ips()
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[!] Auto-Tor closed by user.")
    except ValueError:
        print("Invalid number input.")
