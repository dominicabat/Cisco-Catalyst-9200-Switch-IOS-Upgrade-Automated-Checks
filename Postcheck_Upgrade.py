#Author: John Abat
#Purpose: To do post-checks after upgrading the devices.

import netmiko
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, ReadTimeout
import pprint
import csv
from datetime import datetime
from global_variables import *


#stores credential in variable defined in creds.txt file

with open("creds.txt", mode='r', encoding="utf-8") as cred_file:
    #userpass = cred_file.readlines()
    userpass = [line.strip() for line in cred_file.readlines()]

#print(userpass)
user_name = userpass[0]
pass_word = userpass[1]

#list of commands to be ran on each SW
with open("commands_file_check_upgrade.txt", mode='r', encoding="utf-8") as commands_file:
    list_commands = [line.strip() for line in commands_file.readlines()]


with open("device_list.csv", mode='r', encoding="utf-8") as file:
    list_hosts_ips = dict(csv.reader(file))

rev_list_hosts_ips = {value: key for key, value in list_hosts_ips.items()}
list_hosts = list(rev_list_hosts_ips.keys())

print(rev_list_hosts_ips)
print(list_hosts)


print("=================================================== Starting the script ===================================================")
#iterates each host from the csv -> dict -> list
for host in list_hosts:
    print(f"############################ {host} || {rev_list_hosts_ips[host]} ################################\n\n")
    try:
        connect_param = {
            'device_type': 'cisco_ios',
            'host': host,
            'port': 22,
            'username': user_name,
            'password': pass_word,
        }
        #will be used to create a file containing all data, with timestamp for filename uniqueness.
        timestamp_var = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"Postchecks_{rev_list_hosts_ips[host]}_{timestamp_var}.txt"

        #placeholder out variable to be blank at each host/switch iteration. Output buffer will be appended at each iteration of commands in the next block
        out = ""
        #iterates the commands
        for command in list_commands:
            session_conn = ConnectHandler(**connect_param)
            print(f"\n------------------------------------doing command: {command}...--------------------------------------------------\n")
            out += session_conn.send_command(command, cmd_verify=True, strip_command=False, strip_prompt=False, read_timeout=180)
            print(f"\n----------------------------------------------command: {command} = Success!----------------------------------------------\n")

        #writes the file containing all buffered "out" variable, unique for the host/switch with appended timestamp.
        with open (output_file, "w", encoding="utf-8") as file:
            file.write(out)


        #printing all out variable for Engineer to see in the terminal
        print(out)
        session_conn = ConnectHandler(**connect_param)
        print(f"--------------------verifying if {host} || {rev_list_hosts_ips[host]} is successfully upgraded to {target_version}--------------------\n")
        sh_ver = session_conn.send_command("show version | i Ver", cmd_verify=True, strip_command=False, strip_prompt=False, read_timeout=60)
        print(sh_ver)
        if f"Cisco IOS XE Software, Version {target_version}" in sh_ver:
            print(f"\n{rev_list_hosts_ips[host]} || {host} is successfully upgraded to {target_version}\n")
        else:
            print(f"\n{rev_list_hosts_ips[host]} || {host} upgrade failed to {target_version}\n")


        print("------------------------------------------------------------------------------------------\n")


    #if wrong credential or device took too long to respond, the script will continue to run and print the error encountered.
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(f"{error}\n")

print ("\n\n================================================ End of Script ================================================")