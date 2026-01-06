import requests
from eth_account import Account
from eth_account.messages import encode_defunct
import json
import time
import os
from typing import Optional, List
from datetime import datetime
import pytz
from colorama import Fore, Style, init
import warnings

warnings.filterwarnings('ignore')
init(autoreset=True)

class HumanoidAutoBot:
    def __init__(self, use_proxy=False):
        self.base_url = "https://prelaunch.humanoidnetwork.org/api"
        self.website_url = "https://prelaunch.humanoidnetwork.org"
        self.session = requests.Session()
        self.use_proxy = use_proxy
        self.proxies_list = []
        self.current_proxy_index = 0
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://prelaunch.humanoidnetwork.org",
            "referer": "https://prelaunch.humanoidnetwork.org/user",
            "priority": "u=1, i",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }
        
        if self.use_proxy:
            self.load_proxies()
    
    def load_proxies(self):
        try:
            with open('proxy.txt', 'r') as f:
                self.proxies_list = [line.strip() for line in f.readlines() if line.strip()]
            if self.proxies_list:
                self.log(f"Loaded {len(self.proxies_list)} proxies", "SUCCESS")
            else:
                self.log("No proxies found in proxy.txt", "WARNING")
                self.use_proxy = False
        except FileNotFoundError:
            self.log("proxy.txt not found, running without proxy", "WARNING")
            self.use_proxy = False
        except Exception as e:
            self.log(f"Error loading proxies: {str(e)[:50]}", "ERROR")
            self.use_proxy = False
    
    def get_next_proxy(self):
        if not self.use_proxy or not self.proxies_list:
            return None
        proxy = self.proxies_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies_list)
        
        if proxy.startswith('http://') or proxy.startswith('https://') or proxy.startswith('socks5://'):
            return {
                'http': proxy,
                'https': proxy
            }
        else:
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
    
    def get_wib_time(self):
        wib = pytz.timezone('Asia/Jakarta')
        return datetime.now(wib).strftime('%H:%M:%S')
    
    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()
        
        if level == "INFO":
            color = Fore.CYAN
            symbol = "[INFO]"
        elif level == "SUCCESS":
            color = Fore.GREEN
            symbol = "[SUCCESS]"
        elif level == "ERROR":
            color = Fore.RED
            symbol = "[ERROR]"
        elif level == "WARNING":
            color = Fore.YELLOW
            symbol = "[WARNING]"
        elif level == "CYCLE":
            color = Fore.MAGENTA
            symbol = "[CYCLE]"
        else:
            color = Fore.WHITE
            symbol = "[LOG]"
        
        print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")
    
    def print_banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        banner = f"""
{Fore.CYAN}HUMANOID AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
"""
        print(banner)
    
    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            hours = i // 3600
            minutes = (i % 3600) // 60
            secs = i % 60
            print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)
    
    def scrape_huggingface_models(self, limit: int = 1000) -> List[dict]:
        try:
            self.log("Scraping models from HuggingFace...", "INFO")
            url = "https://huggingface.co/api/models"
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = requests.get(url, proxies=proxy, timeout=30)
            response.raise_for_status()
            models_data = response.json()
            models = []
            for model in models_data[:limit]:
                model_id = model.get('id', '')
                if model_id:
                    models.append({
                        "fileName": model_id,
                        "fileType": "model",
                        "fileUrl": f"https://huggingface.co/{model_id}"
                    })
            self.log(f"Scraped {len(models)} models from HuggingFace", "SUCCESS")
            return models
        except Exception as e:
            self.log(f"Error scraping models: {str(e)[:100]}", "ERROR")
            return self.get_default_models()
    
    def scrape_huggingface_datasets(self, limit: int = 1000) -> List[dict]:
        try:
            self.log("Scraping datasets from HuggingFace...", "INFO")
            url = "https://huggingface.co/api/datasets"
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = requests.get(url, proxies=proxy, timeout=30)
            response.raise_for_status()
            datasets_data = response.json()
            datasets = []
            for dataset in datasets_data[:limit]:
                dataset_id = dataset.get('id', '')
                if dataset_id:
                    datasets.append({
                        "fileName": dataset_id,
                        "fileType": "dataset",
                        "fileUrl": f"https://huggingface.co/datasets/{dataset_id}"
                    })
            self.log(f"Scraped {len(datasets)} datasets from HuggingFace", "SUCCESS")
            return datasets
        except Exception as e:
            self.log(f"Error scraping datasets: {str(e)[:100]}", "ERROR")
            return self.get_default_datasets()
    
    def get_default_models(self) -> list:
        return [
            {"fileName": "microsoft/VibeVoice-Realtime-0.5B", "fileType": "model", 
             "fileUrl": "https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B"},
            {"fileName": "Tongyi-MAI/Z-Image-Turbo", "fileType": "model",
             "fileUrl": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo"},
            {"fileName": "zai-org/GLM-4.6V-Flash", "fileType": "model",
             "fileUrl": "https://huggingface.co/zai-org/GLM-4.6V-Flash"}
        ]
    
    def get_default_datasets(self) -> list:
        return [
            {"fileName": "nvidia/PhysicalAI-Autonomous-Vehicles", "fileType": "dataset",
             "fileUrl": "https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles"},
            {"fileName": "HuggingFaceFW/fineweb-edu", "fileType": "dataset",
             "fileUrl": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu"},
            {"fileName": "OpenGVLab/InternVid", "fileType": "dataset",
             "fileUrl": "https://huggingface.co/datasets/OpenGVLab/InternVid"}
        ]
    
    def get_nonce(self, wallet_address: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/auth/nonce"
            payload = {"walletAddress": wallet_address}
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.post(url, json=payload, headers=self.headers, proxies=proxy, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Nonce error: {str(e)[:50]}", "ERROR")
            return None
    
    def sign_message(self, private_key: str, message: str) -> str:
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            account = Account.from_key(private_key)
            message_hash = encode_defunct(text=message)
            signed_message = account.sign_message(message_hash)
            signature = signed_message.signature.hex()
            if not signature.startswith('0x'):
                signature = '0x' + signature
            return signature
        except Exception as e:
            self.log(f"Signing error: {str(e)[:50]}", "ERROR")
            return None
    
    def authenticate(self, wallet_address: str, message: str, signature: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/auth/authenticate"
            payload = {"walletAddress": wallet_address, "message": message, "signature": signature}
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.post(url, json=payload, headers=self.headers, proxies=proxy, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"Auth error: {str(e)[:50]}", "ERROR")
            return None
    
    def submit_training(self, token: str, item_data: dict) -> Optional[dict]:
        try:
            url = f"{self.base_url}/training"
            headers = self.headers.copy()
            headers["authorization"] = f"Bearer {token}"
            headers["referer"] = "https://prelaunch.humanoidnetwork.org/training"
            payload = {
                "fileName": item_data["fileName"],
                "fileType": item_data["fileType"],
                "fileUrl": item_data["fileUrl"],
                "recaptchaToken": ""
            }
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.post(url, json=payload, headers=headers, proxies=proxy, timeout=30)
            if response.status_code != 200:
                return None
            return response.json()
        except:
            return None
    
    def submit_training_with_unlimited_retry(self, token: str, item_data: dict, retry_delay: int = 5) -> bool:
        attempt = 1
        while True:
            result = self.submit_training(token, item_data)
            if result:
                if attempt > 1:
                    self.log(f"Success after {attempt} attempts!", "SUCCESS")
                return True
            if attempt > 1:
                self.log(f"Retry attempt #{attempt}...", "WARNING")
            time.sleep(retry_delay)
            attempt += 1
    
    def get_items_for_cycle(self, all_items: list, items_per_cycle: int, progress_file: str) -> list:
        try:
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    last_index = int(f.read().strip())
            else:
                last_index = 0
            start_index = last_index
            end_index = start_index + items_per_cycle
            if start_index >= len(all_items):
                start_index = 0
                end_index = items_per_cycle
            selected_items = all_items[start_index:end_index]
            if len(selected_items) < items_per_cycle and start_index > 0:
                remaining = items_per_cycle - len(selected_items)
                selected_items.extend(all_items[0:remaining])
                end_index = remaining
            with open(progress_file, 'w') as f:
                f.write(str(end_index))
            return selected_items
        except Exception as e:
            return all_items[:items_per_cycle]
    
    def get_user_info(self, token: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/user"
            headers = self.headers.copy()
            headers["authorization"] = f"Bearer {token}"
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.get(url, headers=headers, proxies=proxy, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"User info error: {str(e)[:50]}", "ERROR")
            return None
    
    def login(self, private_key: str) -> Optional[str]:
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            account = Account.from_key(private_key)
            wallet_address = account.address
            nonce_response = self.get_nonce(wallet_address)
            if not nonce_response:
                return None
            message = nonce_response.get('message')
            if not message:
                return None
            signature = self.sign_message(private_key, message)
            if not signature:
                return None
            auth_response = self.authenticate(wallet_address, message, signature)
            if not auth_response:
                return None
            token = auth_response.get('token')
            if not token:
                return None
            return token
        except Exception as e:
            self.log(f"Login failed: {str(e)[:50]}", "ERROR")
            return None
    
    def process_account(self, private_key: str, index: int, total: int, models: list, datasets: list) -> bool:
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            account = Account.from_key(private_key)
            wallet_address = account.address
            
            self.log(f"Account #{index}/{total}", "INFO")
            self.log(f"Wallet: {wallet_address[:6]}...{wallet_address[-4:]}", "INFO")
            
            token = self.login(private_key)
            if not token:
                self.log("Login failed", "ERROR")
                return False
            
            self.log("Login successful!", "SUCCESS")
            
            initial_user_info = self.get_user_info(token)
            initial_points = 0
            if initial_user_info:
                initial_points = initial_user_info.get('totalPoints', 0)
                referral_code = initial_user_info.get('user', {}).get('referralCode', 'N/A')
                self.log(f"Initial Points: {initial_points} | Referral: {referral_code}", "INFO")
            
            successful_trainings = 0
            
            self.log(f"Processing {len(models)} models...", "INFO")
            for i, model in enumerate(models, 1):
                model_name = model['fileName'].split('/')[-1][:30]
                self.log(f"Model {i}/{len(models)}: {model_name}", "INFO")
                self.submit_training_with_unlimited_retry(token, model, retry_delay=5)
                self.log(f"Model submitted successfully!", "SUCCESS")
                successful_trainings += 1
                if i < len(models):
                    time.sleep(2)
            
            self.log(f"Processing {len(datasets)} datasets...", "INFO")
            for i, dataset in enumerate(datasets, 1):
                dataset_name = dataset['fileName'].split('/')[-1][:30]
                self.log(f"Dataset {i}/{len(datasets)}: {dataset_name}", "INFO")
                self.submit_training_with_unlimited_retry(token, dataset, retry_delay=5)
                self.log(f"Dataset submitted successfully!", "SUCCESS")
                successful_trainings += 1
                if i < len(datasets):
                    time.sleep(2)
            
            final_user_info = self.get_user_info(token)
            final_points = 0
            points_earned = 0
            
            if final_user_info:
                final_points = final_user_info.get('totalPoints', 0)
                points_earned = final_points - initial_points
            
            total_items = len(models) + len(datasets)
            self.log(f"All tasks completed: {successful_trainings}/{total_items}", "SUCCESS")
            self.log(f"Total Points: {final_points} | Earned: +{points_earned}", "SUCCESS")
            
            return True
        except Exception as e:
            self.log(f"Process error: {str(e)[:50]}", "ERROR")
            return False

def read_accounts(filename: str = "accounts.txt") -> list:
    try:
        with open(filename, 'r') as f:
            accounts = [line.strip() for line in f.readlines() if line.strip()]
        return accounts
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] File {filename} not found!{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error reading file: {e}{Style.RESET_ALL}")
        return []

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""
{Fore.CYAN}HUMANOID AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
{Fore.YELLOW}Select Mode:{Style.RESET_ALL}
{Fore.WHITE}1. Run with proxy{Style.RESET_ALL}
{Fore.WHITE}2. Run without proxy{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
""")
    
    choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
    
    use_proxy = False
    if choice == "1":
        use_proxy = True
    elif choice != "2":
        print(f"{Fore.RED}[ERROR] Invalid choice. Running without proxy.{Style.RESET_ALL}")
        time.sleep(2)
    
    bot = HumanoidAutoBot(use_proxy=use_proxy)
    bot.print_banner()
    
    if use_proxy:
        bot.log("Running with proxy mode", "INFO")
    else:
        bot.log("Running without proxy mode", "INFO")
    
    accounts = read_accounts("accounts.txt")
    if not accounts:
        bot.log("No accounts found in accounts.txt", "ERROR")
        return
    
    bot.log(f"Loaded {len(accounts)} accounts successfully", "SUCCESS")
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}")
    bot.log("Scraping data from HuggingFace...", "INFO")
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    
    all_models = bot.scrape_huggingface_models(limit=1000)
    all_datasets = bot.scrape_huggingface_datasets(limit=1000)
    
    if not all_models:
        bot.log("No models found, using fallback", "WARNING")
        all_models = bot.get_default_models()
    
    if not all_datasets:
        bot.log("No datasets found, using fallback", "WARNING")
        all_datasets = bot.get_default_datasets()
    
    bot.log(f"Total models available: {len(all_models)}", "INFO")
    bot.log(f"Total datasets available: {len(all_datasets)}", "INFO")
    bot.log("Bot will use 3 models + 3 datasets per cycle", "INFO")
    bot.log("Unlimited retry mode enabled", "WARNING")
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
    
    cycle = 1
    total_successful = 0
    total_failed = 0
    
    while True:
        cycle_models = bot.get_items_for_cycle(all_models, 3, 'progress_models.txt')
        cycle_datasets = bot.get_items_for_cycle(all_datasets, 3, 'progress_datasets.txt')
        
        bot.log(f"Cycle #{cycle} Started", "CYCLE")
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        
        bot.log(f"Models: {', '.join([m['fileName'].split('/')[-1][:20] for m in cycle_models])}", "INFO")
        bot.log(f"Datasets: {', '.join([d['fileName'].split('/')[-1][:20] for d in cycle_datasets])}", "INFO")
        
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        
        successful = 0
        failed = 0
        
        for i, private_key in enumerate(accounts, 1):
            if bot.process_account(private_key, i, len(accounts), cycle_models, cycle_datasets):
                successful += 1
                total_successful += 1
            else:
                failed += 1
                total_failed += 1
            
            if i < len(accounts):
                print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                time.sleep(2)
        
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        bot.log(f"Cycle #{cycle} Complete | Success: {successful}/{len(accounts)}", "CYCLE")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
        
        cycle += 1
        
        wait_hours = 24
        wait_seconds = wait_hours * 3600
        bot.countdown(wait_seconds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[ERROR] Program terminated by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n\n{Fore.RED}[ERROR] Fatal error: {e}{Style.RESET_ALL}")
