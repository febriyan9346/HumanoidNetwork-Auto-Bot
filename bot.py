import requests
from eth_account import Account
from eth_account.messages import encode_defunct
import json
import time
import os
from typing import Optional
from datetime import datetime, timedelta
from colorama import Fore, Back, Style, init

init(autoreset=True)

class Colors:
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.CYAN
    HEADER = Fore.MAGENTA
    WALLET = Fore.BLUE
    DATASET = Fore.LIGHTBLUE_EX
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

class TwoCaptchaSolver:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.2captcha.com"
    
    def solve_recaptcha(self, website_url: str, website_key: str) -> Optional[str]:
        try:
            print(f"{Colors.INFO}│  ├─ Solving captcha...{Colors.RESET}")
            
            create_payload = {
                "clientKey": self.api_key,
                "task": {
                    "type": "RecaptchaV2TaskProxyless",
                    "websiteURL": website_url,
                    "websiteKey": website_key,
                    "isInvisible": False
                }
            }
            
            response = requests.post(f"{self.base_url}/createTask", json=create_payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errorId") != 0:
                print(f"{Colors.ERROR}│  ├─ ✗ Captcha error: {result.get('errorDescription')}{Colors.RESET}")
                return None
            
            task_id = result.get("taskId")
            
            max_attempts = 60
            for attempt in range(max_attempts):
                time.sleep(3)
                
                get_payload = {"clientKey": self.api_key, "taskId": task_id}
                response = requests.post(f"{self.base_url}/getTaskResult", json=get_payload)
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status")
                
                if status == "ready":
                    token = result.get("solution", {}).get("gRecaptchaResponse")
                    print(f"{Colors.SUCCESS}│  ├─ ✓ Captcha solved!{Colors.RESET}")
                    return token
                elif status == "processing":
                    if attempt % 10 == 0:
                        print(f"{Colors.INFO}│  ├─ Solving... {attempt * 3}s{Colors.RESET}")
            
            print(f"{Colors.ERROR}│  ├─ ✗ Captcha timeout{Colors.RESET}")
            return None
            
        except Exception as e:
            print(f"{Colors.ERROR}│  ├─ ✗ Captcha error: {str(e)[:50]}{Colors.RESET}")
            return None

class HumanoidAuthBot:
    def __init__(self, captcha_api_key: str):
        self.base_url = "https://prelaunch.humanoidnetwork.org/api"
        self.captcha_solver = TwoCaptchaSolver(captcha_api_key)
        self.website_url = "https://prelaunch.humanoidnetwork.org"
        self.site_key = "6LcdlCcsAAAAAJGvjt5J030ySi7htRzB6rEeBgcP"
        
        self.session = requests.Session()
        
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
    
    def get_nonce(self, wallet_address: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/auth/nonce"
            payload = {"walletAddress": wallet_address}
            response = self.session.post(url, json=payload, headers=self.headers, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            print(f"{Colors.INFO}├─ Nonce received{Colors.RESET}")
            return data
        except Exception as e:
            print(f"{Colors.ERROR}├─ ✗ Nonce error: {str(e)[:100]}{Colors.RESET}")
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
            print(f"{Colors.ERROR}├─ ✗ Signing error: {str(e)[:50]}{Colors.RESET}")
            return None
    
    def authenticate(self, wallet_address: str, message: str, signature: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/auth/authenticate"
            payload = {
                "walletAddress": wallet_address,
                "message": message,
                "signature": signature
            }
            
            response = self.session.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"{Colors.ERROR}├─ ✗ Auth error: {str(e)[:50]}{Colors.RESET}")
            return None
    
    def submit_training(self, token: str, recaptcha_token: str, item_data: dict) -> Optional[dict]:
        try:
            url = f"{self.base_url}/training"
            headers = self.headers.copy()
            headers["authorization"] = f"Bearer {token}"
            headers["referer"] = "https://prelaunch.humanoidnetwork.org/training"
            
            payload = {
                "fileName": item_data["fileName"],
                "fileType": item_data["fileType"],
                "fileUrl": item_data["fileUrl"],
                "recaptchaToken": recaptcha_token
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"{Colors.ERROR}│  └─ ✗ Training error: {str(e)[:50]}{Colors.RESET}")
            return None
    
    def get_training_models(self) -> list:
        try:
            with open('models.txt', 'r') as f:
                models = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) == 2:
                                models.append({
                                    "fileName": parts[0].strip(),
                                    "fileType": "model",
                                    "fileUrl": parts[1].strip()
                                })
                
                if models:
                    return models
        except FileNotFoundError:
            print(f"{Colors.WARNING}├─ models.txt not found, using default models{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.WARNING}├─ Error reading models.txt: {str(e)[:50]}{Colors.RESET}")
        
        return [
            {
                "fileName": "microsoft/VibeVoice-Realtime-0.5B",
                "fileType": "model",
                "fileUrl": "https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B"
            },
            {
                "fileName": "Tongyi-MAI/Z-Image-Turbo",
                "fileType": "model",
                "fileUrl": "https://huggingface.co/Tongyi-MAI/Z-Image-Turbo"
            },
            {
                "fileName": "zai-org/GLM-4.6V-Flash",
                "fileType": "model",
                "fileUrl": "https://huggingface.co/zai-org/GLM-4.6V-Flash"
            }
        ]
    
    def get_training_datasets(self) -> list:
        try:
            with open('datasets.txt', 'r') as f:
                datasets = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) == 2:
                                datasets.append({
                                    "fileName": parts[0].strip(),
                                    "fileType": "dataset",
                                    "fileUrl": parts[1].strip()
                                })
                
                if datasets:
                    return datasets
        except FileNotFoundError:
            print(f"{Colors.WARNING}├─ datasets.txt not found, using default datasets{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.WARNING}├─ Error reading datasets.txt: {str(e)[:50]}{Colors.RESET}")
        
        return [
            {
                "fileName": "nvidia/PhysicalAI-Autonomous-Vehicles",
                "fileType": "dataset",
                "fileUrl": "https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles"
            },
            {
                "fileName": "HuggingFaceFW/fineweb-edu",
                "fileType": "dataset",
                "fileUrl": "https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu"
            },
            {
                "fileName": "OpenGVLab/InternVid",
                "fileType": "dataset",
                "fileUrl": "https://huggingface.co/datasets/OpenGVLab/InternVid"
            }
        ]
    
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
            print(f"{Colors.ERROR}[!] Error managing progress: {e}{Colors.RESET}")
            return all_items[:items_per_cycle]
    
    def get_user_info(self, token: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/user"
            headers = self.headers.copy()
            headers["authorization"] = f"Bearer {token}"
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"{Colors.ERROR}├─ ✗ User info error: {str(e)[:50]}{Colors.RESET}")
            return None
    
    def login(self, private_key: str) -> Optional[str]:
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            account = Account.from_key(private_key)
            wallet_address = account.address
            
            print(f"{Colors.INFO}├─ Getting nonce...{Colors.RESET}")
            nonce_response = self.get_nonce(wallet_address)
            if not nonce_response:
                return None
            
            message = nonce_response.get('message')
            if not message:
                return None
            
            print(f"{Colors.INFO}├─ Signing message...{Colors.RESET}")
            signature = self.sign_message(private_key, message)
            if not signature:
                return None
            
            print(f"{Colors.INFO}├─ Authenticating...{Colors.RESET}")
            auth_response = self.authenticate(wallet_address, message, signature)
            if not auth_response:
                return None
            
            token = auth_response.get('token')
            if not token:
                return None
            
            print(f"{Colors.SUCCESS}├─ ✓ Login successful!{Colors.RESET}")
            
            print(f"{Colors.INFO}├─ Getting user info...{Colors.RESET}")
            user_info = self.get_user_info(token)
            if user_info:
                points = user_info.get('points', 0)
                referral_code = user_info.get('referralCode', 'N/A')
                print(f"{Colors.SUCCESS}├─ ✓ Points: {points} | Referral: {referral_code}{Colors.RESET}")
            
            return token
            
        except Exception as e:
            print(f"{Colors.ERROR}├─ ✗ Login failed: {str(e)[:50]}{Colors.RESET}")
            return None
    
    def process_account(self, private_key: str, index: int, total: int, models: list, datasets: list) -> bool:
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            account = Account.from_key(private_key)
            wallet_address = account.address
            
            print(f"\n{Colors.HEADER}{'─' * 60}{Colors.RESET}")
            print(f"{Colors.HEADER}Account {index}/{total}{Colors.RESET}")
            print(f"{Colors.WALLET}Wallet: {wallet_address}{Colors.RESET}")
            print(f"{Colors.HEADER}{'─' * 60}{Colors.RESET}")
            
            token = self.login(private_key)
            if not token:
                print(f"{Colors.ERROR}└─ ✗ Process failed at login{Colors.RESET}")
                return False
            
            successful_trainings = 0
            failed_trainings = 0
            
            print(f"\n{Colors.INFO}┌─ Starting MODEL submissions ({len(models)} models){Colors.RESET}")
            
            for i, model in enumerate(models, 1):
                print(f"{Colors.INFO}│{Colors.RESET}")
                print(f"{Colors.INFO}├─ Model {i}/{len(models)}: {model['fileName']}{Colors.RESET}")
                
                recaptcha_token = self.captcha_solver.solve_recaptcha(
                    self.website_url,
                    self.site_key
                )
                
                if not recaptcha_token:
                    print(f"{Colors.ERROR}│  └─ ✗ Captcha failed{Colors.RESET}")
                    failed_trainings += 1
                    continue
                
                print(f"{Colors.SUCCESS}│  ├─ ✓ Captcha solved{Colors.RESET}")
                print(f"{Colors.INFO}│  ├─ Submitting model...{Colors.RESET}")
                
                training_response = self.submit_training(token, recaptcha_token, model)
                
                if training_response:
                    print(f"{Colors.SUCCESS}│  └─ ✓ Model submitted!{Colors.RESET}")
                    successful_trainings += 1
                else:
                    print(f"{Colors.ERROR}│  └─ ✗ Model submission failed{Colors.RESET}")
                    failed_trainings += 1
                
                if i < len(models):
                    time.sleep(2)
            
            print(f"\n{Colors.DATASET}┌─ Starting DATASET submissions ({len(datasets)} datasets){Colors.RESET}")
            
            for i, dataset in enumerate(datasets, 1):
                print(f"{Colors.DATASET}│{Colors.RESET}")
                print(f"{Colors.DATASET}├─ Dataset {i}/{len(datasets)}: {dataset['fileName']}{Colors.RESET}")
                
                recaptcha_token = self.captcha_solver.solve_recaptcha(
                    self.website_url,
                    self.site_key
                )
                
                if not recaptcha_token:
                    print(f"{Colors.ERROR}│  └─ ✗ Captcha failed{Colors.RESET}")
                    failed_trainings += 1
                    continue
                
                print(f"{Colors.SUCCESS}│  ├─ ✓ Captcha solved{Colors.RESET}")
                print(f"{Colors.DATASET}│  ├─ Submitting dataset...{Colors.RESET}")
                
                training_response = self.submit_training(token, recaptcha_token, dataset)
                
                if training_response:
                    print(f"{Colors.SUCCESS}│  └─ ✓ Dataset submitted!{Colors.RESET}")
                    successful_trainings += 1
                else:
                    print(f"{Colors.ERROR}│  └─ ✗ Dataset submission failed{Colors.RESET}")
                    failed_trainings += 1
                
                if i < len(datasets):
                    time.sleep(2)
            
            total_items = len(models) + len(datasets)
            print(f"{Colors.INFO}│{Colors.RESET}")
            print(f"{Colors.INFO}└─ Training Summary:{Colors.RESET}")
            print(f"   {Colors.SUCCESS}✓ Successful: {successful_trainings}/{total_items}{Colors.RESET}")
            print(f"   {Colors.ERROR}✗ Failed: {failed_trainings}/{total_items}{Colors.RESET}")
            
            return successful_trainings > 0
                
        except Exception as e:
            print(f"{Colors.ERROR}└─ ✗ Process error: {str(e)[:50]}{Colors.RESET}")
            return False

def read_file(filename: str) -> Optional[str]:
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()
        return content if content else None
    except FileNotFoundError:
        print(f"{Colors.ERROR}[!] File {filename} not found!{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.ERROR}[!] Error reading file {filename}: {e}{Colors.RESET}")
        return None

def read_accounts(filename: str = "accounts.txt") -> list:
    try:
        with open(filename, 'r') as f:
            accounts = [line.strip() for line in f.readlines() if line.strip()]
        return accounts
    except FileNotFoundError:
        print(f"{Colors.ERROR}[!] File {filename} not found!{Colors.RESET}")
        return []
    except Exception as e:
        print(f"{Colors.ERROR}[!] Error reading file: {e}{Colors.RESET}")
        return []

def print_banner():
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════╗
║                HUMANOID NETWORK AUTO BOT                ║
╚═══════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)

def create_default_files():
    if not os.path.exists('models.txt'):
        default_models = """# Humanoid Network Training Models
# Format: fileName|fileUrl
# Add one model per line

microsoft/VibeVoice-Realtime-0.5B|https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B
Tongyi-MAI/Z-Image-Turbo|https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
zai-org/GLM-4.6V-Flash|https://huggingface.co/zai-org/GLM-4.6V-Flash

# Add more models below
# username/model-name|https://huggingface.co/username/model-name
"""
        try:
            with open('models.txt', 'w') as f:
                f.write(default_models)
            print(f"{Colors.SUCCESS}✓ Created default models.txt{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.ERROR}[!] Error creating models.txt: {e}{Colors.RESET}")
    
    if not os.path.exists('datasets.txt'):
        default_datasets = """# Humanoid Network Training Datasets
# Format: fileName|fileUrl
# Add one dataset per line

nvidia/PhysicalAI-Autonomous-Vehicles|https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles
HuggingFaceFW/fineweb-edu|https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu
OpenGVLab/InternVid|https://huggingface.co/datasets/OpenGVLab/InternVid

# Add more datasets below
# username/dataset-name|https://huggingface.co/datasets/username/dataset-name
"""
        try:
            with open('datasets.txt', 'w') as f:
                f.write(default_datasets)
            print(f"{Colors.SUCCESS}✓ Created default datasets.txt{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.ERROR}[!] Error creating datasets.txt: {e}{Colors.RESET}")

def print_summary(successful: int, failed: int, total: int, cycle_num: int):
    print(f"\n{Colors.HEADER}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}CYCLE {cycle_num} SUMMARY{Colors.RESET}")
    print(f"{Colors.HEADER}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.INFO}Total Accounts  : {total}{Colors.RESET}")
    print(f"{Colors.SUCCESS}Successful      : {successful}{Colors.RESET}")
    print(f"{Colors.ERROR}Failed          : {failed}{Colors.RESET}")
    print(f"{Colors.WARNING}Success Rate    : {(successful/total*100):.1f}%{Colors.RESET}")
    print(f"{Colors.HEADER}{'═' * 60}{Colors.RESET}\n")

def countdown_timer(seconds: int, message: str):
    end_time = datetime.now() + timedelta(seconds=seconds)
    
    while True:
        remaining = (end_time - datetime.now()).total_seconds()
        if remaining <= 0:
            break
        
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        secs = int(remaining % 60)
        
        timer_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        print(f"\r{Colors.WARNING}{message} {timer_str}{Colors.RESET}", end="", flush=True)
        time.sleep(1)
    
    print(f"\r{Colors.SUCCESS}{message} Complete!{Colors.RESET}" + " " * 20)

def main():
    print_banner()
    
    create_default_files()
    
    captcha_api_key = read_file("2captcha.txt")
    if not captcha_api_key:
        print(f"{Colors.ERROR}[!] No API key found in 2captcha.txt{Colors.RESET}")
        return
    
    print(f"{Colors.SUCCESS}✓ 2Captcha API Key loaded{Colors.RESET}")
    
    accounts = read_accounts("accounts.txt")
    if not accounts:
        print(f"{Colors.ERROR}[!] No accounts found in accounts.txt{Colors.RESET}")
        return
    
    print(f"{Colors.SUCCESS}✓ Loaded {len(accounts)} account(s){Colors.RESET}")
    
    bot = HumanoidAuthBot(captcha_api_key)
    
    all_models = bot.get_training_models()
    all_datasets = bot.get_training_datasets()
    
    if not all_models:
        print(f"{Colors.ERROR}[!] No models found{Colors.RESET}")
        return
    
    if not all_datasets:
        print(f"{Colors.ERROR}[!] No datasets found{Colors.RESET}")
        return
    
    print(f"{Colors.SUCCESS}✓ Loaded {len(all_models)} total models{Colors.RESET}")
    print(f"{Colors.SUCCESS}✓ Loaded {len(all_datasets)} total datasets{Colors.RESET}")
    print(f"{Colors.INFO}ℹ Bot will use 3 models + 3 datasets per cycle (rotates automatically){Colors.RESET}")
    
    cycle_num = 1
    total_successful = 0
    total_failed = 0
    
    while True:
        cycle_models = bot.get_items_for_cycle(all_models, 3, 'progress_models.txt')
        cycle_datasets = bot.get_items_for_cycle(all_datasets, 3, 'progress_datasets.txt')
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BOLD}STARTING CYCLE {cycle_num}{Colors.RESET}")
        print(f"{Colors.INFO}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        
        print(f"{Colors.WARNING}\nModels for this cycle:{Colors.RESET}")
        for i, model in enumerate(cycle_models, 1):
            print(f"{Colors.WARNING}  {i}. {model['fileName']}{Colors.RESET}")
        
        print(f"{Colors.DATASET}\nDatasets for this cycle:{Colors.RESET}")
        for i, dataset in enumerate(cycle_datasets, 1):
            print(f"{Colors.DATASET}  {i}. {dataset['fileName']}{Colors.RESET}")
        
        print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 60}{Colors.RESET}")
        
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
                time.sleep(3)
        
        print_summary(successful, failed, len(accounts), cycle_num)
        
        print(f"{Colors.HEADER}{'─' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}TOTAL STATS (All Cycles){Colors.RESET}")
        print(f"{Colors.SUCCESS}Total Successful: {total_successful}{Colors.RESET}")
        print(f"{Colors.ERROR}Total Failed    : {total_failed}{Colors.RESET}")
        print(f"{Colors.HEADER}{'─' * 60}{Colors.RESET}\n")
        
        cycle_num += 1
        wait_hours = 24
        wait_seconds = wait_hours * 3600
        
        print(f"{Colors.WARNING}Waiting {wait_hours} hours before next cycle...{Colors.RESET}")
        countdown_timer(wait_seconds, "Next cycle in:")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}[!] Bot stopped by user{Colors.RESET}")
    except Exception as e:
        print(f"\n\n{Colors.ERROR}[!] Fatal error: {e}{Colors.RESET}")
