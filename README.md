# Humanoid Network Auto Bot

## 🔗 Register Here
**Join Humanoid Network**: https://prelaunch.humanoidnetwork.org/ref/68CMPK

---

An automated bot for Humanoid Network training submissions. This bot handles authentication, captcha solving, and model training submissions automatically.

## 🌟 Features

- ✅ Automatic wallet authentication
- ✅ Multi-account support
- ✅ Automatic model rotation (3 models per cycle)
- ✅ 24-hour cycle automation
- ✅ Progress tracking
- ✅ Colored console output
- ✅ Detailed logging and statistics

## 📋 Prerequisites

- Python 3.7 or higher
- Ethereum private keys
- Internet connection

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/febriyan9346/HumanoidNetwork-Auto-Bot.git
cd HumanoidNetwork-Auto-Bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure your files (see Configuration section below)

## ⚙️ Configuration

### 1. accounts.txt
Add your Ethereum private keys (one per line):
```
0x1234567890abcdef...
0xabcdef1234567890...
```

⚠️ **Security Warning**: Never share your private keys! Keep this file secure.

### Basic Usage
Run the main bot:
```bash
python bot.py
```

The bot will:
1. Load your accounts and API key
2. Process each account sequentially
3. Submit 3 models & 3 datasets per account per cycle
4. Rotate to the next 3 models & 3 datasets in the next cycle
5. Wait 24 hours before starting a new cycle
6. Repeat indefinitely

## 📊 How It Works

**Authentication**:
   - Gets nonce from API
   - Signs message with private key
   - Authenticates and receives token

## 📈 Statistics

The bot provides detailed statistics:
- Per-account success/failure rates
- Per-cycle summaries
- Total accumulated statistics
- Real-time progress updates

## ⏰ Timing

- **Per account**: ~3-6 minutes (3 models)
- **Cycle interval**: 24 hours

## ⚠️ Disclaimer

This bot is for educational purposes. Use at your own risk. Always:
- Keep your private keys secure
- Use dedicated wallets for automation
- Follow Humanoid Network's terms of service

## 🐛 Troubleshooting

**Authentication fails:**
- Verify your private key format
- Ensure private key starts with `0x`
- Check API connectivity

## 📝 License

MIT License - feel free to modify and distribute.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 💬 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Made with ❤️ for the Humanoid Network community**

Register here: https://prelaunch.humanoidnetwork.org/ref/68CMPK
