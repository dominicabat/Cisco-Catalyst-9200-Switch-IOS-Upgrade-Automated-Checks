#Author: John Abat
#Purpose: To do pre-work prior to Image transfer. Check flash: contents, remove inactive pkg files in flash; check if scp server is enabled on switch, configure if not yet.
#Restriction: DO NOT run this script for devices already containing the target image (17.15.5). Install remove inactive will delete it from flash

import netmiko
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, ReadTimeout
import pprint
import csv


#stores credential in variable defined in creds.txt file

with open("creds.txt", mode='r', encoding="utf-8") as cred_file:
    #userpass = cred_file.readlines()
    userpass = [line.strip() for line in cred_file.readlines()]

#print(userpass)
user_name = userpass[0]
pass_word = userpass[1]



#list of commands to be ran on each SW
with open("commands_file_pre_work.txt", mode='r', encoding="utf-8") as commands_file:
    list_commands = [line.strip() for line in commands_file.readlines()]


with open("device_list.csv", mode='r', encoding="utf-8") as file:
    list_hosts_ips = dict(csv.reader(file))
    #print(list_hosts_ips) - for tshoot purposes

#csv file is in "hostname:ip" format, make sense when inputting the data.
#I reversed the key, value pair so that the IP would be the key and the hostname would be the value
#The reason I reversed that is because there are certain part of the code that I want the key to be iterated, and that key would be used to produce the value. 
#This is a limitation of dictionary where (key->value). But it can't do the other way around (value -> key) as I intended for the structure of code. :D

rev_list_hosts_ips = {value: key for key, value in list_hosts_ips.items()}
list_hosts = list(rev_list_hosts_ips.keys())


print("==================================== Starting the script ==================================================")
#iterates each host from the CSV -> dict -> list of IPs
for host in list_hosts:
    print(f"##############################{host} || {rev_list_hosts_ips[host]}################################\n\n")
    try:
        connect_param = {
            'device_type': 'cisco_ios',
            'host': host,
            'port': 22,
            'username': user_name,  
            'password': pass_word,  
        }

        #iterates the commands
        for command in list_commands:
            session_conn = ConnectHandler(**connect_param)
            print(f"\n----------------------------doing command: {command}---------------------------------------\n")

            #executes command 'dir flash:'
            if command == 'dir flash:':
                out = session_conn.send_command(command, cmd_verify=True, strip_command=False, strip_prompt=False)
                print (out)

            #checks if scp server is already running on the switch, if not, configures it then saves config.
            elif command == 'sh run | i scp server':
                out = session_conn.send_command(command)
                if out == "ip scp server enable":
                    print("SCP is already enabled on this device")
                elif out != "ip scp server enable":
                    print("SCP is not yet enabled, enabling SCP in the device...")
                    cli_conf = session_conn.send_config_set("ip scp server enable", strip_command=False, strip_prompt=False)
                    cli_conf += session_conn.save_config()
                    print (cli_conf)
                    print ("\n!!!SCP is now enabled!!!")


            #removes inactive pkg / image files in flash. Other flash doesn't have anything to clean so if it doesn't match the expect string, prompting [y/n], then it executes the exception block instead.
            #if there's an inactive image to clean, then the prompt would reach the [y/n], then script would send 'y'. If not, then there's nothing to clean, it would not receive the expected prompt in "expect_string", would encounter the exception
            elif command == 'install remove inactive':
                try:
                    out = session_conn.send_command(command, strip_command=False, strip_prompt=False, expect_string=r"Do you want to remove the above files\?")
                    out += session_conn.send_command("y", strip_command=False, strip_prompt=False, read_timeout=60, expect_string = r"#")
                    print (out)
                except (ReadTimeout) as e:
                    print("!!!Switch doesn't have any inactive images, skipping this step...!!!")
                    print("--------------------see exception error below-------------------")
                    print(e)

            #failsafe, this will only be printed if none of the above if/elif are executed. In the current iterated command
            else:
                print("check if there's something wrong in var:list_commands:")





#if wrong credential or device took too long to respond the script will continue to run and print the error encountered.
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(f"{error}\n")




print ("\n\n=========================== End of Script ==========================================")