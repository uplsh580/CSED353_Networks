import subprocess
import sys
import time

def package_install(package):
    while (1):
        print("This program needs [{}] package.".format(package))
        reply = input("Is it okay to install [{}] package? (y/n) : ".format(package))
        if reply == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            time.sleep(1)
            return True
        elif reply == 'n':
            print("Quit program.")
            exit()

if __name__ == "__main__":
    #Check paramiko package
    try:
        import paramiko
    except ImportError as e:
        os.system('clear')
        package_install("paramiko")