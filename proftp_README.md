# 🔐 ProFTP – FTP Password Cracking Toolkit

> **"When speed meets precision – crack FTP logins with style."**

ProFTP is a Python-based toolkit for **FTP credential brute-forcing**.  
It includes both **Basic** and **Advanced** cracking modes, giving you flexibility between quick tests and more extensive, mutation-based attacks.

---

## ⚠️ Disclaimer
This tool is intended for **educational and authorized penetration testing only**.  
Do **NOT** use it against systems without explicit permission. The author is not responsible for any misuse.

---

## ✨ Features

### **Basic Mode (`basic.py`)**
- Single username, password list–based brute-force
- Multi-threaded for faster execution
- Simple and quick for small tests

### **Advanced Mode (`adv.py`)**
- Supports **multiple usernames** and password lists
- Optional **wordlist mutation** for stronger attacks (`--mutate` flag)
- Multi-threaded with a job queue
- Tries common variations (leet speak, suffixes like `123`, `!`, `2024`, etc.)
- Handles more complex cracking scenarios

---

## 📂 Project Structure

```
proftp/
├── basic.py       # Basic FTP brute-force script
├── adv.py         # Advanced FTP brute-force script
├── user.txt       # Example list of usernames (for testing)
├── pass.txt       # Example list of passwords (for testing)
└── README.md      # You're reading it!
```

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/err0rgod/proftp.git
   cd proftp
   ```

2. **Ensure Python 3 is installed**
   ```bash
   python3 --version
   ```

3. **No external dependencies** — uses Python's built-in libraries.

---

## 🚀 Usage

### **Basic Mode**
Brute-force a single username against a password list:
```bash
python3 basic.py -ho <host> -u <username> -p pass.txt -t 30
```
**Arguments:**
- `-ho` / `--host` → Target FTP server IP/hostname
- `-u` / `--user` → Username to try
- `-p` / `--passfile` → Password list file
- `-t` / `--threads` → (Optional) Number of threads (default: 20)

---

### **Advanced Mode**
Brute-force multiple usernames with optional password mutation:
```bash
python3 adv.py -ho <host> -u user.txt -p pass.txt -t 30 --mutate
```
**Arguments:**
- `-ho` / `--host` → Target FTP server IP/hostname
- `-u` / `--user` → File containing usernames (one per line)
- `-p` / `--passfile` → Password list file
- `-t` / `--threads` → (Optional) Number of threads (default: 20)
- `-m` / `--mutate` → Enable wordlist mutation for stronger attacks

---

## 🔍 Example
```bash
# Basic mode
python3 basic.py -ho 192.168.1.10 -u admin -p pass.txt

# Advanced mode with mutation
python3 adv.py -ho 192.168.1.10 -u user.txt -p pass.txt --mutate
``

**Sample Output:**
```
 The Password was Found and Connection was Success
 Connect with 192.168.1.10 as admin  :   password123
```

---

## 📜 License
Released under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 👤 Author
**err0rgod** – [GitHub Profile](https://github.com/err0rgod)  
10x Dev | IoT Hacker | Malware Dev | Red Teamer | Python/C/C++ | AI/ML | IoT | Robotics
