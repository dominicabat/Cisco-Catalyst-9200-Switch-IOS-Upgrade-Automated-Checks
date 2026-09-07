#Author: John Abat
#Purpose: To do pre-checks before upgrading the devices.


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



#list of commands to verify hash / checksum
list_commands_imgverify = [
 f'verify /md5 flash:{target_image} {md5_checksum}',
 f'verify /sha512 flash:{target_image} {sha512_checksum}']


#have to define the verify commands within python and not in the text file due to f string limitation. I wanted the target_image and md5_checksum to be a changeable variable depending on what's being upgraded. 
#to do that, the normal show commands will be on the text file, the verify command (or any command that uses f string) will be defined within python then 'extended' to the list_commands list to be iterated by the for loop later on.

list_commands.extend(list_commands_imgverify)






print("========================================== Starting the script =====================================================")
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
        output_file = F"Prechecks_{rev_list_hosts_ips[host]}:{timestamp_var}.txt"

        #placeholder out variable to be blank at each host/switch iteration. Output buffer will be appended at each iteration of commands in the next block
        out = ""
        #iterates the commands
        for command in list_commands:
            session_conn = ConnectHandler(**connect_param)
            print(f"\n-----------------------------doing command: {command}...-------------------------------------------------\n")
            out += session_conn.send_command(command, cmd_verify=True, strip_command=False, strip_prompt=False, read_timeout=180)
            print(f"\n-------------------------------------------------------command: {command} = Success!--------------------------------------------\n")

        #writes the file containing all buffered "out" variable, unique for the host/switch with appended timestamp.
        with open (output_file, 'w', encoding="utf-8") as file:
            file.write(out)


        #printing all out variable for Engineer to see in the terminal
        print(out)
        print("-------------------------------------------------------------------------------------------------------------------")


        #this will serve as additional layer of verification to compare the MD5 and SHA512 Hash. You may manually verify in the output of the precheck file or in "out"
        for imgverify in list_commands_imgverify:
            session_conn_ver = ConnectHandler(**connect_param)
            print(f"\n-----------------------------doing verify command: {imgverify}...--------------------------------------------------\n")
            out_verify = session_conn_ver.send_command(imgverify, cmd_verify=True, strip_command=False, strip_prompt=False, read_timeout=180)
            if imgverify == f'verify /md5 flash:{target_image} {md5_checksum}':
                if f"Verified (flash:{target_image}) = {md5_checksum}" in out_verify:
                    print ("MD5 Checksum matches! Double check if SHA512 will match\n")
                else:
                    print("Image is corrupted, delete the target image then transfer it again to the switch\n")

            if imgverify == f'verify /sha512 flash:{target_image} {sha512_checksum}':
                if f"Verified (flash:{target_image}) = {sha512_checksum}" in out_verify:
                    print ("SHA512 Checksum matches! Engineer may now proceed with the upgrade\n")
                else:
                    print("Image is corrupted, delete the target image then transfer it again to the switch\n")

        print("-------------------------------------------------------------------------------------------------------------------")
        print (f"\n\n\nPrechecks done for {host} || {rev_list_hosts_ips[host]}")
        print (f"Prechecks file saved as {output_file}\n\n")


    #if wrong credential or device took too long to respond, the script will continue to run and print the error encountered.
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(f"{error}\n")

print ("\n\n========================================= End of Script ======================================================")