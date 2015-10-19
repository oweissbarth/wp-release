#!/usr/bin/env python
import sys
import os.path
import re
import zipfile
import tempfile
import logging
import paramiko
import ConfigParser
from scp import SCPClient

def main():
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
    check_config()
    wp_release()


def check_config():
    global config
    config = ConfigParser.RawConfigParser()
    home = os.path.expanduser("~")
    logging.info("Checking for configuration file at "+home) 
    if len(config.read(os.path.join(home, ".wp-release")))!=1:
        logging.warn("No configuration file found. Attempting to create one")
        
        config.add_section("config")
        config.set("config", "SERVER_NAME", raw_input("Enter release-server name or ip: "))
        config.set("config", "USER_NAME", raw_input("Enter your ssh username: "))
        config.set("config", "SSH_KEY", raw_input("Enter the path to your ssh-key: "))
        config.set("config", "REMOTE_DEST_DIR_PLUGINS", raw_input("Enter the path the remote release directory for plugins: "))
        config.set("config", "REMOTE_DEST_DIR_THEMES", raw_input("Enter the path the remote release directory for themes: "))
        
        with open(os.path.join(home,'.wp-release'), 'wb') as configfile:
            config.write(configfile)
        logging.info("Created configuration file. Proceeding...")
    else:
        logging.info("Found configuration file. Proceeding...")
        

def wp_release():
    global config

    logging.info("Checking asset directory...")

    if len(sys.argv) != 2:
      logging.error("Please specify asset path!")
      sys.exit(1)

    if not os.path.isdir(sys.argv[1]):
      logging.error("Asset directory not found!")
      sys.exit(1)

    asset_dir = os.path.normpath(os.path.abspath(sys.argv[1]))

    asset_name = os.path.basename(os.path.normpath(os.path.abspath(sys.argv[1])))

    logging.info("done.")

    path_array = asset_dir.split(os.sep)
    asset_type = path_array[len(path_array)-2]

    if asset_type not in ["themes", "plugins"]:
        logging.error("We currently don't support releasing of type "+asset_type)
        sys.exit(1)
            


    logging.info("Detected type "+asset_type[:-1])



    logging.info("Determining asset version...")
    #determine version
    asset_version = ""

    if asset_type=="plugins":
        file = open (os.path.join(asset_dir, asset_name+".php"), "r")
    else:
        file = open (os.path.join(asset_dir,"style.css"), "r")

    for line in file:
      if re.match(".*Version:.*\n", line):
        asset_version = re.sub(".*Version:", "", line).strip()
        
    logging.info("done.")
    logging.info("Preparing to release "+asset_name+" at version " +asset_version)


    # create zip
    logging.info("Creating archive...")

    zipf = zipfile.ZipFile(os.path.join(tempfile.gettempdir(),asset_name+".zip"), "w")
    zipdir(asset_dir, zipf)
    zipf.close()


    archive_name = asset_name+".zip"

    logging.info("done.")



    #uploading
    logging.info("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(config.get("config", "SERVER_NAME"), username=config.get("config", "USER_NAME"), key_filename=config.get("config", "SSH_KEY"))
    logging.info("done.")

    logging.info("Uploading archive...")
    scp = SCPClient(ssh.get_transport())

    scp.put(os.path.join(tempfile.gettempdir(), archive_name))
    logging.info("done.")


    if asset_type=="plugins":
        REMOTE_DEST_DIR = config.get("config", "REMOTE_DEST_DIR_PLUGINS")
    else:
        REMOTE_DEST_DIR = config.get("config", "REMOTE_DEST_DIR_THEMES")


    (stdin, stdout, stderr) = ssh.exec_command("mv "+archive_name+" "+REMOTE_DEST_DIR)
    if stdout.channel.recv_exit_status() != 0:
        logging.error("Error while moving archive on remote server")
        for line in stderr.readlines():
            print line 
        sys.exit(1)
        
    (stdin, stdout, stderr) = ssh.exec_command("sed -i 's/.*\"version\": .*/\t\"version\": \""+asset_version+"\",/' "+REMOTE_DEST_DIR+asset_name+ ".json")
    if stdout.channel.recv_exit_status() != 0:
        logging.error("Error while updating version number")
        for line in stderr.readlines():
            print line 
        sys.exit(1)

    #clean up
    logging.info("Closing connection...")
    ssh.close()
    logging.info("done.")
    
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        files = [f for f in files if not f[0] == '.' and not f[-1]=='~']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, os.pardir)))          
