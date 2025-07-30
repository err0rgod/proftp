import ftplib
import argparse



parser = argparse.ArgumentParser(description="Basic FTP tester")

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