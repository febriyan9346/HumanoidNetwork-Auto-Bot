from curl_cffi import requests
from eth_account import Account
from eth_account.messages import encode_defunct
import time
import os
import random
from datetime import datetime
import pytz
from colorama import Fore, Style, init
import warnings

warnings.filterwarnings('ignore')
init(autoreset=True)

class HumanoidAutoBot:
    def __init__(self, use_proxy=False):
        self.base_url = "https://prelaunch.humanoidnetwork.org/api"
        self.use_proxy = use_proxy
        self.proxies_list = []
        self.current_proxy_index = 0
        self.session = requests.Session(impersonate="chrome124")
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://prelaunch.humanoidnetwork.org",
            "referer": "https://prelaunch.humanoidnetwork.org/",
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
    
    def get_next_proxy(self):
        if not self.use_proxy or not self.proxies_list:
            return None
        proxy = self.proxies_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies_list)
        
        if proxy.startswith('http://') or proxy.startswith('https://') or proxy.startswith('socks5://'):
            return {'http': proxy, 'https': proxy}
        else:
            return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
    
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
    
    def get_nonce(self, wallet_address):
        try:
            url = f"{self.base_url}/auth/nonce"
            payload = {"walletAddress": wallet_address}
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.post(url, json=payload, headers=self.headers, proxies=proxy, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.log(f"Nonce error: {str(e)[:50]}", "ERROR")
            return None
    
    def sign_message(self, private_key, message):
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
    
    def authenticate(self, wallet_address, message, signature):
        try:
            url = f"{self.base_url}/auth/authenticate"
            payload = {
                "walletAddress": wallet_address, 
                "message": message, 
                "signature": signature,
                "referralCode": "9CPNN0"
            }
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.post(url, json=payload, headers=self.headers, proxies=proxy, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.log(f"Auth error: {str(e)[:50]}", "ERROR")
            return None
    
    def submit_training(self, token, item_data):
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
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def scrape_huggingface_models(self):
        try:
            self.log("Scraping models from HuggingFace...", "INFO")
            url = "https://huggingface.co/api/models"
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.get(url, proxies=proxy, timeout=30)
            if response.status_code == 200:
                models_data = response.json()
                models = []
                for model in models_data[:1000]:
                    if model.get('id'):
                        models.append({
                            "fileName": model['id'],
                            "fileType": "model",
                            "fileUrl": f"https://huggingface.co/{model['id']}"
                        })
                self.log(f"Scraped {len(models)} models from HuggingFace", "SUCCESS")
                return models
            raise Exception("Failed to scrape")
        except:
            return self.get_default_models()

    def scrape_huggingface_datasets(self):
        try:
            self.log("Scraping datasets from HuggingFace...", "INFO")
            url = "https://huggingface.co/api/datasets"
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.get(url, proxies=proxy, timeout=30)
            if response.status_code == 200:
                datasets_data = response.json()
                datasets = []
                for dataset in datasets_data[:1000]:
                    if dataset.get('id'):
                        datasets.append({
                            "fileName": dataset['id'],
                            "fileType": "dataset",
                            "fileUrl": f"https://huggingface.co/datasets/{dataset['id']}"
                        })
                self.log(f"Scraped {len(datasets)} datasets from HuggingFace", "SUCCESS")
                return datasets
            raise Exception("Failed to scrape")
        except:
            return self.get_default_datasets()

    def get_default_models(self):
        return [
            {"fileName": "microsoft/VibeVoice-Realtime-0.5B", "fileType": "model", "fileUrl": "https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B"},
            {"fileName": "Tongyi-MAI/Z-Image-Turbo", "fileType": "model", "fileUrl": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo"},
            {"fileName": "zai-org/GLM-4.6V-Flash", "fileType": "model", "fileUrl": "https://huggingface.co/zai-org/GLM-4.6V-Flash"}
        ]
    
    def get_default_datasets(self):
        return [
            {"fileName": "nvidia/PhysicalAI-Autonomous-Vehicles", "fileType": "dataset", "fileUrl": "https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles"},
            {"fileName": "HuggingFaceFW/fineweb-edu", "fileType": "dataset", "fileUrl": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu"},
            {"fileName": "OpenGVLab/InternVid", "fileType": "dataset", "fileUrl": "https://huggingface.co/datasets/OpenGVLab/InternVid"}
        ]

    def get_user_info(self, token):
        try:
            url = f"{self.base_url}/user"
            headers = self.headers.copy()
            headers["authorization"] = f"Bearer {token}"
            proxy = self.get_next_proxy() if self.use_proxy else None
            response = self.session.get(url, headers=headers, proxies=proxy, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.log(f"User info error: {str(e)[:50]}", "ERROR")
            return None

    def login(self, private_key):
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
            
        return auth_response.get('token')

    def submit_items(self, token, items, target_count, item_type):
        successful_count = 0
        random.shuffle(items)
        
        for item in items:
            if successful_count >= target_count:
                break
                
            item_name = item['fileName'].split('/')[-1][:30]
            self.log(f"Trying {item_type}: {item_name}", "INFO")
            
            result = self.submit_training(token, item)
            if result:
                self.log(f"{item_type.capitalize()} submitted successfully!", "SUCCESS")
                successful_count += 1
                time.sleep(2)
            else:
                self.log(f"Failed to submit {item_name}, trying next...", "WARNING")
        
        return successful_count

    def process_account(self, private_key, index, total, all_models, all_datasets, run_mode, models_per_account, datasets_per_account):
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
            
            models_submitted = 0
            datasets_submitted = 0
            
            if run_mode in ["models", "all"]:
                self.log(f"Processing models (target: {models_per_account})...", "INFO")
                models_submitted = self.submit_items(token, all_models, models_per_account, "model")
            
            if run_mode in ["datasets", "all"]:
                self.log(f"Processing datasets (target: {datasets_per_account})...", "INFO")
                datasets_submitted = self.submit_items(token, all_datasets, datasets_per_account, "dataset")
            
            final_user_info = self.get_user_info(token)
            final_points = 0
            points_earned = 0
            
            if final_user_info:
                final_points = final_user_info.get('totalPoints', 0)
                points_earned = final_points - initial_points
            
            total_submitted = models_submitted + datasets_submitted
            target_total = 0
            if run_mode in ["models", "all"]:
                target_total += models_per_account
            if run_mode in ["datasets", "all"]:
                target_total += datasets_per_account
            
            self.log(f"All tasks completed: {total_submitted}/{target_total}", "SUCCESS")
            self.log(f"Total Points: {final_points} | Earned: +{points_earned}", "SUCCESS")
            
            return True
        except Exception as e:
            self.log(f"Process error: {str(e)[:50]}", "ERROR")
            return False

def read_accounts(filename="accounts.txt"):
    try:
        with open(filename, 'r') as f:
            accounts = [line.strip() for line in f.readlines() if line.strip()]
        return accounts
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] File {filename} not found!{Style.RESET_ALL}")
        return []

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""
{Fore.CYAN}HUMANOID AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
{Fore.YELLOW}Select Proxy Mode:{Style.RESET_ALL}
{Fore.WHITE}1. Run with proxy{Style.RESET_ALL}
{Fore.WHITE}2. Run without proxy{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
""")
    
    proxy_choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
    
    use_proxy = False
    if proxy_choice == "1":
        use_proxy = True
    elif proxy_choice != "2":
        print(f"{Fore.RED}[ERROR] Invalid choice. Running without proxy.{Style.RESET_ALL}")
        time.sleep(2)
    
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""
{Fore.CYAN}HUMANOID AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
{Fore.YELLOW}Select Run Mode:{Style.RESET_ALL}
{Fore.WHITE}1. Run models only{Style.RESET_ALL}
{Fore.WHITE}2. Run datasets only{Style.RESET_ALL}
{Fore.WHITE}3. Run all (models + datasets){Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
""")
    
    mode_choice = input(f"{Fore.GREEN}Enter your choice (1/2/3): {Style.RESET_ALL}").strip()
    
    run_mode = "all"
    if mode_choice == "1":
        run_mode = "models"
    elif mode_choice == "2":
        run_mode = "datasets"
    elif mode_choice == "3":
        run_mode = "all"
    else:
        print(f"{Fore.RED}[ERROR] Invalid choice. Running all mode.{Style.RESET_ALL}")
        time.sleep(2)
    
    bot = HumanoidAutoBot(use_proxy=use_proxy)
    bot.print_banner()
    
    if use_proxy:
        bot.log("Running with proxy mode", "INFO")
    else:
        bot.log("Running without proxy mode", "INFO")
    
    if run_mode == "models":
        bot.log("Run Mode: MODELS ONLY", "INFO")
    elif run_mode == "datasets":
        bot.log("Run Mode: DATASETS ONLY", "INFO")
    else:
        bot.log("Run Mode: ALL (Models + Datasets)", "INFO")
    
    accounts = read_accounts("accounts.txt")
    if not accounts:
        bot.log("No accounts found in accounts.txt", "ERROR")
        return
    
    bot.log(f"Loaded {len(accounts)} accounts successfully", "SUCCESS")
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}")
    bot.log("Scraping data from HuggingFace...", "INFO")
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    
    all_models = []
    all_datasets = []
    
    if run_mode in ["models", "all"]:
        all_models = bot.scrape_huggingface_models()
        bot.log(f"Total models available: {len(all_models)}", "INFO")
    
    if run_mode in ["datasets", "all"]:
        all_datasets = bot.scrape_huggingface_datasets()
        bot.log(f"Total datasets available: {len(all_datasets)}", "INFO")
    
    if run_mode == "models":
        bot.log("Bot will use 3 models per account", "INFO")
    elif run_mode == "datasets":
        bot.log("Bot will use 3 datasets per account", "INFO")
    else:
        bot.log("Bot will use 3 models + 3 datasets per account", "INFO")
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
    
    cycle = 1
    
    while True:
        bot.log(f"Cycle #{cycle} Started", "CYCLE")
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        
        successful = 0
        failed = 0
        
        for i, private_key in enumerate(accounts, 1):
            if bot.process_account(private_key, i, len(accounts), all_models, all_datasets, run_mode, 3, 3):
                successful += 1
            else:
                failed += 1
            
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
