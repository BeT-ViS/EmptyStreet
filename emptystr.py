import requests
import threading
import random
import time
import os
import sys

# ==== COLOR CODES ====
R = '\033[31m'
G = '\033[32m'
Y = '\033[33m'
C = '\033[36m'
W = '\033[0m'

# ==== EFFECTS ====
colors = [R, G, Y, C]

def typing_effect(text, delay=0.01):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_animation(text="Loading", duration=3):
    print()
    for _ in range(duration * 2):
        for frame in ["|", "/", "-", "\\"]:
            sys.stdout.write(f"\r{Y}{text}... {frame}{W}")
            sys.stdout.flush()
            time.sleep(0.2)
    print(f"\r{G}{text}... done!{W}\n")

def progress_bar(current, total, width=40):
    ratio = current / total
    bar = "█" * int(ratio * width) + "-" * (width - int(ratio * width))
    sys.stdout.write(f"\r{C}[{bar}] {current}/{total} proxies scanned{W}")
    sys.stdout.flush()

# ==== BANNER ====
def print_banner():
    os.system("clear")
    banner = f"""{G}
███████╗███╗   ███╗██████╗ ████████╗██╗   ██╗    ███████╗████████╗██████╗ ███████╗███████╗████████╗
██╔════╝████╗ ████║██╔══██╗╚══██╔══╝╚██╗ ██╔╝    ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝
█████╗  ██╔████╔██║██████╔╝   ██║    ╚████╔╝     ███████╗   ██║   ██████╔╝█████╗  █████╗     ██║   
██╔══╝  ██║╚██╔╝██║██╔═══╝    ██║     ╚██╔╝      ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══╝     ██║   
███████╗██║ ╚═╝ ██║██║        ██║      ██║       ███████║   ██║   ██║  ██║███████╗███████╗   ██║   
╚══════╝╚═╝     ╚═╝╚═╝        ╚═╝      ╚═╝       ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   

                           {Y}CLI Version by DDK™{W}
"""
    print(banner)

def boot_system():
    typing_effect(f"{C}[BOOT] Initializing EMPTY STREET engine...", 0.02)
    typing_effect(f"{C}[BOOT] Loading proxy scanner modules...", 0.02)
    typing_effect(f"{C}[BOOT] Checking network access...", 0.02)
    typing_effect(f"{G}[✓] All systems online.{W}", 0.02)

# ==== PROXY FUNCTIONS ====

def get_socks_proxies():
    url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.text.strip().splitlines()
    except:
        pass
    return []

def check_proxy(proxy):
    try:
        res = requests.get("http://httpbin.org/ip", proxies={
            "http": f"socks5h://{proxy}",
            "https": f"socks5h://{proxy}"
        }, timeout=10)
        if res.status_code == 200:
            return proxy, True
    except:
        pass
    return proxy, False

def get_my_ip(proxy=None):
    try:
        proxies = {
            "http": f"socks5h://{proxy}",
            "https": f"socks5h://{proxy}"
        } if proxy else None

        res = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
        return res.json().get("origin", "Unknown")
    except:
        return "Unavailable"

# ==== PROXY SCAN ====

def process_proxies():
    typing_effect(f"{Y}[*] Fetching underground SOCKS5 proxies...{W}", 0.01)
    proxies = get_socks_proxies()
    if not proxies:
        print(f"{R}[-] Failed to fetch proxy list.{W}")
        return []

    typing_effect(f"{C}[+] {len(proxies)} proxies retrieved. Scanning top 300...{W}", 0.01)
    alive_proxies = []
    total = min(300, len(proxies))
    count = 0
    lock = threading.Lock()

    def worker(proxy):
        nonlocal count
        proxy, alive = check_proxy(proxy)
        with lock:
            count += 1
            progress_bar(count, total)
        color = random.choice(colors)
        if alive:
            alive_proxies.append(proxy)
            typing_effect(f"\n{color}⚡ [✓] Live Proxy: {proxy}{W}", 0.003)
        else:
            typing_effect(f"\n{R}☠ [x] Dead Proxy: {proxy}{W}", 0.001)

    threads = []
    for proxy in proxies[:total]:
        t = threading.Thread(target=worker, args=(proxy,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print()
    with open("alive_proxies.txt", "w") as f:
        for p in alive_proxies:
            f.write(p + "\n")

    print(f"{G}[✓] {len(alive_proxies)} working proxies saved to alive_proxies.txt{W}")
    return alive_proxies

# ==== AUTO GHOST MODE ====

def auto_ghost_mode(proxies):
    print(f"{Y}[+] Auto Ghost Mode activated — rotating every 30s{W}")
    try:
        while True:
            proxy = random.choice(proxies)
            print(f"\n{C}→ [Ghost] Using: {proxy}{W}")
            ip = get_my_ip(proxy)
            print(f"{G}✓ [IP] Current: {ip}{W}")
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"\n{R}[!] Auto Ghost stopped.{W}")

# ==== MAIN ====

if __name__ == "__main__":
    loading_animation("Launching EMPTY STREET", duration=3)
    print_banner()
    boot_system()
    proxies = process_proxies()
    if proxies:
        choice = input(f"{Y}[*] Start Auto Ghost Mode? (y/n): {W}").strip().lower()
        if choice == "y":
            auto_ghost_mode(proxies)
