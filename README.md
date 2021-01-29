Description
===========
Automatization of VMware ESXi VMs snapshots peridically creating and removing for planning updates


Requirements
============
1) python >= 3.6

2) python module pyvmomi: Python SDK for the VMware vSphere API


Installation
============
1) Clone pyvmsnap repo to directory /usr/local/orbit on your VMware management host:
```
sudo mkdir -p /usr/local/orbit
cd /usr/local/orbit
sudo git clone https://github.com/pavlovdo/pyvmsnap
```

2) A) Check execute permissions for scripts:
```
ls -l *.py *.sh
```
B) If not:
```
sudo chmod +x *.py *.sh
```

3) Change example configuration file pyvmsnap.conf: login, password, IP address of vcenter;

4) Change example configuration file vms.conf: names of VMs for which snapshots will be created and removed;

5) Further you have options: run scripts from host or run scripts from docker container.

If you want to run scripts from host:

A) Install Python 3 and pip3 if it is not installed;

B) Install required python modules:
```
pip3 install -r requirements.txt
```

C) Plan creating and removing snapshots for your ESXi VMs and create cron jobs:
```
echo "00 03 * * 6 /usr/local/orbit/pyvmsnap/pyvmsnap.py create > /usr/local/orbit/pyvmsnap/data/output" > /tmp/crontab && \
echo "00 03 * * 3 /usr/local/orbit/pyvmsnap/pyvmsnap.py remove > /usr/local/orbit/pyvmsnap/data/output" >> /tmp/crontab && \
crontab /tmp/crontab && rm /tmp/crontab
```

If you want to run scripts from docker container:

A) Run build.sh:
```
cd /usr/local/orbit/pyvmsnap
./build.sh
```

B) Run dockerrun.sh;
```
./dockerrun.sh
```


Tested
======
Tested with VMware ESXi 6.x


Related Links
=============
https://github.com/vmware/pyvmomi
