# Cisco-Catalyst-9200-Switch-IOS-Upgrade-Automated-Checks
Automating Preliminary work, Prechecks, and Postchecks when doing IOS Upgrades to 9200/9300 Catalyst Switches

## Overview
Automating
- the preliminary work such as configuring device to act as an SCP server, removing inactive image files in flash:
- the prechecks, backup the config, get the network state, and check the image's md5 and sha512 hash
- the postchecks, network state after the config and ensure the device operates as intended post-upgrade.

## Usage
### Input the data in **device_list.csv**. _Hostname,IP_ format. You can define multiple devices here to speed up the work. 
```
hostname_001,10.1.1.1
hostname_002,10.1.1.2
```

### Read the release notes before deciding which IOS version to proceed. Common considerations are upgrade path and specific ROMMON version before proceeding to jump from 1 version to another. 
- [9200 release notes](https://www.cisco.com/c/en/us/support/switches/catalyst-9200-r-series-switches/products-release-notes-list.html)
- [9300 release notes](https://www.cisco.com/c/en/us/support/switches/catalyst-9300-series-switches/products-release-notes-list.html)


### Define the global variables in **global_variables.py**. This depends on your target IOS version and the specific md5 and sha512 checksum of the image file.
```
#global variables

target_image = 'cat9k_lite_iosxe.17.15.05.SPA.bin'
target_version = '17.15.05'
md5_checksum = '2c45a0c8d3c3957484957f3cdcfa551e'
sha512_checksum = '314dc2160b39c09626f2f541e2043fa781f9ea817a46524ac897d3e8ec48333760c69b59a2591362dc288c4f0f281241b3498125f287ba2e4f61162afb3f3ab'
```


- Note: to get the image file, go to https://software.cisco.com/download/home/286319845 and navigate what specific catalyst platform are you using.
- for demonstration purposes, choose IOS XE software for [Catalyst 9200-48T Switch](https://software.cisco.com/download/home/286320181/type/282046477/release/IOSXE-17.18.4) considering the upgrade path, release notes, and caveats.


### Define the commands in **commands_file_pre_work.txt** to do the pre-work before proceeding to do image transfer towards the Switch
```
dir flash:
sh run | i scp server
install remove inactive
```

-these commands are going to be executed following the logic defined in **Pre-Work.py**


### Run the **Pre-Work.py** to remove inactive images and configure the switch as an scp server if it isn't configured yet. 
```
py Pre-Work.py
```


### Transfer the image from local pc to the switch via [scp](https://www.cisco.com/c/en/us/support/docs/security-vpn/secure-shell-ssh/215450-copy-cisco-ios-images-from-pc-to-router.html)

```
scp -O ios_filename username@<ip_address_of_the_device>:ios_filename
```

### Input the list of commands that you want to check in the switch before proceeding to upgrade in **commands_file_check_upgrade.txt**
```
show ip route
show ip arp
show mac add
dir bootflash:
show lic sum
sh version
sh platform
show boot
show switch
sh cdp neigh
sh clock
```

### Manually upgrade the Switch
- [9200 upgrade process - INSTALL mode](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9200-series-switches/222282-upgrading-catalyst-9200-switches.html#toc-hId--1726690856)
- [9300 upgrade process - INSTALL mode](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9300-series-switches/222280-upgrading-catalyst-9300-switches.html#toc-hId--1922252130)


_Note: I haven't developed an automated way to do the actual upgrade process yet, for now, I'm opting to do manual. This will be updated in the near future once I have a test case to do so_

```
install add file flash:<file_name>.bin activate commit
```
- The thing to note here is that this command takes too long to process. It takes quite a time before it asks you to proceed with the [y/n] question to proceed and reload in the send_command() function of NetMiko.
- The solution that I'm thinking is to set the read_timeout parameter to more than 10 mins or 600 seconds
- I was contemplating in an Engineering decision whether it would be practical to automate the actual upgrade process or stick to manual.
- I do plan to automate it once I have a test case, but it would upgrade the switches 1 by 1 instead of all at the same time.


### Run the Postcheck_Upgrade.py to do the postchecks once upgrade is done
```
py Postcheck_Upgrade.py
```


# Author
[John Dominic Abat](https://github.com/dominicabat/)
