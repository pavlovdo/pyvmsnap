#!/usr/bin/env python3

#
# VMware ESXi VMs creating and removing snapshots
#
# 2018-2021 Denis Pavlov
#

import atexit
import argparse
import os
import sys
import time
import ssl

from configread import configread
from pyVmomi import vim, vmodl
from pyVim.task import WaitForTask
from pyVim import connect
from pyVim.connect import Disconnect, SmartConnect, GetSi


# set config file name
conf_file = '/usr/local/orbit/pyvmsnap/conf.d/pyvmsnap.conf'

vcenter_parameters = configread(conf_file, 'vCenter', 'ip', 'login',
                                'password', 'ignore_ssl',
                                'vms_list_file', 'snapshot_name')

parser = argparse.ArgumentParser(
    description='Create or remove ESXi VMs snapshots')
parser.add_argument('operation', metavar='operation',
                    help='create or remove snapshots')
args = parser.parse_args()
print(args.operation)


def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def list_snapshots_recursively(snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (
            snapshot.name, snapshot.description,
            snapshot.createTime, snapshot.state)
        snapshot_data.append(snap_text)
        snapshot_data = snapshot_data + list_snapshots_recursively(
            snapshot.childSnapshotList)
    return snapshot_data


def get_snapshots_by_name_recursively(snapshots, snapname):
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.name == snapname:
            snap_obj.append(snapshot)
        else:
            snap_obj = snap_obj + get_snapshots_by_name_recursively(
                snapshot.childSnapshotList, snapname)
    return snap_obj


def get_current_snap_obj(snapshots, snapob):
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.snapshot == snapob:
            snap_obj.append(snapshot)
        snap_obj = snap_obj + get_current_snap_obj(
            snapshot.childSnapshotList, snapob)
    return snap_obj


def main():

    print("Trying to connect to vCenter...")

    if vcenter_parameters['ignore_ssl'] and hasattr(ssl, "_create_unverified_context"):
        context = ssl._create_unverified_context()

    conn = connect.SmartConnect(host=vcenter_parameters['ip'], port=443,
                                user=vcenter_parameters['login'],
                                pwd=vcenter_parameters['password'],
                                sslContext=context)

    atexit.register(Disconnect, conn)

    print("Connected to vCenter !")

    content = conn.RetrieveContent()
    operation = args.operation

    vms_list_file = open(vcenter_parameters['vms_list_file'])
    for vm in vms_list_file:
        vm_name = vm.strip()
        vm = get_obj(content, [vim.VirtualMachine], vm_name)

        if not vm:
            print("Virtual Machine %s doesn't exists" % vm_name)
            sys.exit()

        if operation != 'create' and vm.snapshot is None:
            print("Virtual Machine %s doesn't have any snapshots" % vm.name)
            continue

        if operation == 'create':
            snapshot_name = vcenter_parameters['snapshot_name']
            description = "Before update snapshot"
            dumpMemory = False
            quiesce = False

            print("Creating snapshot %s for virtual machine %s\n" % (
                snapshot_name, vm.name))
            WaitForTask(vm.CreateSnapshot(
                snapshot_name, description, dumpMemory, quiesce))

        elif operation in ['remove', 'revert']:
            snapshot_name = vcenter_parameters['snapshot_name']
            snap_obj = get_snapshots_by_name_recursively(
                vm.snapshot.rootSnapshotList, snapshot_name)
            # if len(snap_obj) is 0; then no snapshots with specified name
            if len(snap_obj) == 1:
                snap_obj = snap_obj[0].snapshot
                if operation == 'remove':
                    print("Removing snapshot %s for virtual machine %s\n" % (
                        snapshot_name, vm.name))
                    WaitForTask(snap_obj.RemoveSnapshot_Task(True))
                else:
                    print("Reverting to snapshot %s" % snapshot_name)
                    WaitForTask(snap_obj.RevertToSnapshot_Task())
            else:
                print("No snapshots found with name: %s on VM: %s\n" % (
                    snapshot_name, vm.name))

        elif operation == 'list_all':
            print("Display list of snapshots on virtual machine %s" % vm.name)
            snapshot_paths = list_snapshots_recursively(
                vm.snapshot.rootSnapshotList)
            for snapshot in snapshot_paths:
                print(snapshot)

        elif operation == 'list_current':
            current_snapref = vm.snapshot.currentSnapshot
            current_snap_obj = get_current_snap_obj(
                vm.snapshot.rootSnapshotList, current_snapref)
            current_snapshot = "Name: %s; Description: %s; " \
                               "CreateTime: %s; State: %s" % (
                                   current_snap_obj[0].name,
                                   current_snap_obj[0].description,
                                   current_snap_obj[0].createTime,
                                   current_snap_obj[0].state)
            print("Virtual machine %s current snapshot is:" % vm.name)
            print(current_snapshot)

        elif operation == 'remove_all':
            print("Removing all snapshots for virtual machine %s" % vm.name)
            WaitForTask(vm.RemoveAllSnapshots())

        else:
            print("Specify operation in "
                  "create/remove/revert/list_all/list_current/remove_all")


# Start program
if __name__ == "__main__":
    main()
