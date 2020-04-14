#!/usr/bin/env python3.8

# python script using Netmiko to connect to device
# Get show output from devices and save to a txt file under a folder
# To use : thuang$ ./configbackup.py cisco_commands.txt cisco.json

import netmiko
import json
import os
import sys
import signal
import smtplib
import usernamepassword
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import date
today = date.today().strftime("%m-%d-%Y")

netmiko_exceptions = (netmiko.ssh_exception.NetMikoAuthenticationException,
                        netmiko.ssh_exception.NetmikoTimeoutException)

username = usernamepassword.username
password = usernamepassword.password
emailpassword = usernamepassword.emailpassword

with open('cisco_commands.txt') as cmd_file:
    commands = cmd_file.readlines()

with open('cisco.json') as dev_file:
    devices = json.load(dev_file)

for device in devices:
    device['username'] = username
    device['password'] = password

    try:
        print('~'*79)
        print('Connecting to device', device['ip'])

        connection = netmiko.ConnectHandler(**device)
        dir_path = os.path.join('/Users/thuang/Documents/9, Config Backup', today, connection.base_prompt + '_' + device['ip'])

        text = connection.base_prompt
        appendFile = open (today + ' devicebackup.txt' , 'a')
        appendFile.write('\n')
        appendFile.write(text)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            print("Directory Already Exists")

        for command in commands:
            filename = command.strip().replace(' ', '_') + '.txt'

            with open(os.path.join(dir_path, filename), 'w') as out_file:
                out_file.write(connection.send_command(command) + '\n')

        connection.disconnect()
        appendFile.close()

    except netmiko_exceptions as e:
        print('authentication failed to', device['ip'], e)

##### email config backup result ####

file = open(today + ' devicebackup.txt', 'r')
f = file.read()

email_user = 'tohuang@outlook.com'
email_send = 'netops@heartflow.com'
subject = 'Network Devices Config Backup Completed on ' + today

msg = MIMEMultipart ()
msg ['From'] = email_user
msg ['To'] = email_send
msg ['subject'] = subject

body ='Configuration back up successful for the following devices : ' + f
msg.attach(MIMEText(body,'plain'))

text = msg.as_string()
server = smtplib.SMTP('smtp-mail.outlook.com',587)
server.starttls()
server.login(email_user,emailpassword)

server.sendmail (email_user,email_send,text)
server.quit()
