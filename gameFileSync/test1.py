import os
import subprocess

ret = os.system("D:/soft/cwRsync/bin/rsync.exe -aczr --delete --progress /cygdrive/f/test /cygdrive/e")
#subprocess.call("D:\soft\cwRsync\\bin\\rsync.exe -aczr --delete --progress /cygdrive/f/test /cygdrive/e")

print(ret)