import ftplib
import argparse



parser = argparse.ArgumentParser(description="Basic FTP tester")


parser.add_argument("-h","--host",required=True, type=str, help="Enter the target to test ftp")
parser.add_argument("-p","--passfile",required=True,type=str,help="Enter the path of file containing password list")
parser.add_argument("-t","--threads",type=int,help="enter the number of threads")

host = "test.rebex.net"
user = "demo"
password = "password"

try:
    with ftplib.FTP() as serve:
        serve.connect(host,21,timeout=5)
        serve.login(user,password)
        print(f"Connection Successfull with {host} by {user}  :   {password}")


except Exception as e:
    print(f"Connection failed with {user}  :   {password}")