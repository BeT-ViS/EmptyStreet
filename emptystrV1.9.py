import curses
import requests
import threading
import random
import time
from datetime import datetime

# === Fake headers ===
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.68.0",
    "EmptyStreet-Scanner/1.0",
    "HackerBot/9.9",
    "Googlebot/2.1 (+http://www.google.com/bot.html)"
]

# === Shared state ===
alive_proxies = []
dead_count = 0
current_proxy = ""
current_ip = ""
auto_ghost_running = True

def get_socks_proxies():
    url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.text.strip().splitlines()
    except:
        return []
    return []

def check_proxy(proxy):
    global dead_count
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        res = requests.get("http://httpbin.org/ip", proxies={
            "http": f"socks5h://{proxy}",
            "https": f"socks5h://{proxy}"
        }, headers=headers, timeout=8)
        if res.status_code == 200:
            return proxy, True
    except:
        pass
    dead_count += 1
    return proxy, False

def get_my_ip(proxy=None):
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        proxies = {
            "http": f"socks5h://{proxy}",
            "https": f"socks5h://{proxy}"
        } if proxy else None

        res = requests.get("http://httpbin.org/ip", proxies=proxies, headers=headers, timeout=8)
        return res.json().get("origin", "Unknown")
    except:
        return "Unavailable"

def log_ip_change(proxy, ip):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] Switched to proxy: {proxy} | IP: {ip}\n"
    with open("ghostlog.txt", "a") as f:
        f.write(log_line)

def auto_ghost(stdscr):
    global current_proxy, current_ip, auto_ghost_running
    while auto_ghost_running:
        if not alive_proxies:
            time.sleep(1)
            continue
        proxy = random.choice(alive_proxies)
        ip = get_my_ip(proxy)
        current_proxy = proxy
        current_ip = ip
        log_ip_change(proxy, ip)
        time.sleep(30)

def draw_ui(stdscr):
    global alive_proxies, dead_count, current_proxy, current_ip, auto_ghost_running

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.clear()

    stdscr.addstr(0, 2, "EMPTY STREET - CLI Version by DDK™", curses.A_BOLD)
    stdscr.addstr(1, 2, "-" * 60)

    # Scan proxies
    stdscr.addstr(3, 2, "[*] Fetching SOCKS5 proxies...")
    stdscr.refresh()
    proxies = get_socks_proxies()

    stdscr.addstr(4, 2, f"[+] {len(proxies)} proxies retrieved. Checking top 300...")
    stdscr.refresh()

    lock = threading.Lock()
    count = 0
    total = min(300, len(proxies))

    def worker(proxy):
        nonlocal count
        proxy, ok = check_proxy(proxy)
        with lock:
            count += 1
            percent = int((count / total) * 100)
            stdscr.addstr(6, 2, f"[SCAN] Progress: {count}/{total} ({percent}%)")
            stdscr.refresh()
        if ok:
            alive_proxies.append(proxy)

    threads = []
    for proxy in proxies[:total]:
        t = threading.Thread(target=worker, args=(proxy,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Save proxies
    with open("alive_proxies.txt", "w") as f:
        for p in alive_proxies:
            f.write(p + "\n")

    stdscr.addstr(8, 2, f"[✓] {len(alive_proxies)} live proxies saved.")
    stdscr.addstr(9, 2, "[+] Press 'q' to quit, auto ghost is running...", curses.A_BOLD)

    # Start auto ghost thread
    ghost_thread = threading.Thread(target=auto_ghost, args=(stdscr,), daemon=True)
    ghost_thread.start()

    while True:
        stdscr.addstr(11, 2, f"[LIVE PROXIES] {len(alive_proxies)}")
        stdscr.addstr(12, 2, f"[DEAD PROXIES] {dead_count}")
        stdscr.addstr(14, 2, f"[ACTIVE PROXY] {current_proxy}")
        stdscr.addstr(15, 2, f"[MASKED IP   ] {current_ip}")
        stdscr.refresh()

        try:
            key = stdscr.getch()
            if key == ord('q'):
                auto_ghost_running = False
                break
            time.sleep(0.5)
        except:
            continue

def main():
    curses.wrapper(draw_ui)

if __name__ == "__main__":
    main()
