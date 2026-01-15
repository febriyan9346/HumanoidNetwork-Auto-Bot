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

    def complete_social_tasks(self, token):
        self.log("Checking and completing social tasks...", "INFO")
        
        tasks_list = [
            {"id": "1", "name": "Follow HAN on X", "data": {"url": "https://x.com/HumanoidNetwork"}},
            {"id": "2", "name": "Join Telegram Community", "data": {"url": "https://t.me/TheHumanoidNetwork"}},
            {"id": "3", "name": "Share on Social Media", "data": {}},
            {"id": "5", "name": "Join our Discord", "data": {"url": "https://discord.gg/f5C32A89q8"}},
            {"id": "6", "name": "Follow on Instagram", "data": {"url": "https://www.instagram.com/humanoidnetwork?igsh=MWIwZmpoZnQ5ZGh5bw=="}},
            {"id": "7", "name": "Subscribe on YouTube", "data": {"url": "https://www.youtube.com/@HumanoidNetwork"}},
            {"id": "8", "name": "Follow on TikTok", "data": {"url": "https://www.tiktok.com/@humanoidnetwork?is_from_webapp=1&sender_device=pc"}},
            {"id": "9", "name": "Join our Reddit", "data": {"url": "https://www.reddit.com/user/humanoidNetwork/"}}
        ]

        tasks_list.sort(key=lambda x: int(x["id"]))

        headers = self.headers.copy()
        headers["authorization"] = f"Bearer {token}"
        url = f"{self.base_url}/tasks"

        for task in tasks_list:
            try:
                payload = {
                    "taskId": task["id"],
                    "data": task["data"]
                }
                
                proxy = self.get_next_proxy() if self.use_proxy else None
                response = self.session.post(url, json=payload, headers=headers, proxies=proxy, timeout=20)
                
                if response.status_code == 200:
                    resp_json = response.json()
                    if resp_json.get("completed"):
                        self.log(f"Task {task['id']} ({task['name']}) -> COMPLETED", "SUCCESS")
                    else:
                        self.log(f"Task {task['id']} ({task['name']}) -> ALREADY DONE", "SUCCESS")
                elif response.status_code == 400:
                    self.log(f"Task {task['id']} ({task['name']}) -> ALREADY COMPLETED", "SUCCESS")
                else:
                    self.log(f"Task {task['id']} ({task['name']}) -> ERROR {response.status_code}", "WARNING")
                
                time.sleep(1)
            except Exception as e:
                self.log(f"Task {task['id']} ({task['name']}) -> FAILED: {str(e)[:30]}", "WARNING")

    def get_training_progress(self, token):
        try:
            url = f"{self.base_url}/training/progress"
            headers = self.headers.copy()
            headers["authorization"] = f"Bearer {token}"
            proxy = self.get_next_proxy() if self.use_proxy else None
            
            response = self.session.get(url, headers=headers, proxies=proxy, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.log(f"Progress check error: {str(e)[:50]}", "ERROR")
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
                return models
            raise Exception("Failed to scrape")
        except:
            return self.get_default_models()

    def scrape_huggingface_datasets(self):
        try:
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
        
        items_to_try = items[:target_count + 5]
        
        for item in items_to_try:
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

    def process_account(self, private_key, index, total, all_models, all_datasets):
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

            self.complete_social_tasks(token)
            
            progress_data = self.get_training_progress(token)
            
            models_remaining = 3
            datasets_remaining = 3
            
            if progress_data:
                models_remaining = progress_data['daily']['models']['remaining']
                datasets_remaining = progress_data['daily']['datasets']['remaining']
                self.log(f"Status: {models_remaining} Models left | {datasets_remaining} Datasets left", "INFO")
            else:
                self.log("Failed to fetch progress, assuming full limit (3/3)", "WARNING")

            initial_user_info = self.get_user_info(token)
            initial_points = 0
            if initial_user_info:
                initial_points = initial_user_info.get('totalPoints', 0)
                self.log(f"Current Points: {initial_points}", "INFO")
            
            if models_remaining > 0:
                self.log(f"Processing {models_remaining} models...", "INFO")
                self.submit_items(token, all_models, models_remaining, "model")
            else:
                self.log("Daily Models task already completed! Skipping...", "SUCCESS")
            
            if datasets_remaining > 0:
                self.log(f"Processing {datasets_remaining} datasets...", "INFO")
                self.submit_items(token, all_datasets, datasets_remaining, "dataset")
            else:
                self.log("Daily Datasets task already completed! Skipping...", "SUCCESS")
            
            final_user_info = self.get_user_info(token)
            final_points = 0
            points_earned = 0
            
            if final_user_info:
                final_points = final_user_info.get('totalPoints', 0)
                points_earned = final_points - initial_points
            
            self.log(f"Account processing finished", "SUCCESS")
            self.log(f"Total Points: {final_points} | Earned in this run: +{points_earned}", "SUCCESS")
            
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
        pass
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}")
    
    bot = HumanoidAutoBot(use_proxy=use_proxy)
    
    if use_proxy:
        bot.log("Running with proxy mode", "INFO")
    else:
        bot.log("Running without proxy mode", "INFO")
    
    accounts = read_accounts("accounts.txt")
    if not accounts:
        bot.log("No accounts found in accounts.txt", "ERROR")
        return
    
    bot.log(f"Loaded {len(accounts)} accounts successfully", "SUCCESS")
    
    all_models = bot.scrape_huggingface_models()
    all_datasets = bot.scrape_huggingface_datasets()
    
    cycle = 1
    
    while True:
        bot.log(f"Cycle #{cycle} Started", "CYCLE")
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        
        successful = 0
        failed = 0
        
        for i, private_key in enumerate(accounts, 1):
            if bot.process_account(private_key, i, len(accounts), all_models, all_datasets):
                successful += 1
            else:
                failed += 1
            
            if i < len(accounts):
                print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                time.sleep(1)
        
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
