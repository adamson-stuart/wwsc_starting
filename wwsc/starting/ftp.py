from ftplib import FTP
import json
import threading


def upload_file(local_file, remote_file):
    upload_thread = threading.Thread(target=inner_upload_file,daemon=True, args=(local_file, remote_file))
    upload_thread.start()

def inner_upload_file(local_file, remote_file):
    with open("config.json","r") as handle:
        config = json.load(handle)

    ftp=FTP(config["FTP"]["Server"])
    ftp.login(config["FTP"]["Username"],config["FTP"]["Password"])
    with open(local_file,"rb") as handle:
        print ("Uploading "+local_file+" to "+remote_file)
        ftp.storbinary("STOR "+remote_file,handle)
        print ("Uploaded "+local_file+" to "+remote_file)
    ftp.close()
