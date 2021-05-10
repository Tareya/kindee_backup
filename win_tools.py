# -*- coding: utf-8 -*-

import os, platform, datetime, wmi

'''windows 工具类'''
class windows_tools:

    '''类初始化'''
    def __init__(self):
        self.computer = wmi.wmi()


    '''系统信息'''
    def system_info(self):
        pass


    '''cpu信息'''
    def cpu_info(self):
        pass


    '''cpu使用率'''
    def cpu_usage(self):
        pass


    '''内存信息'''
    def memory_info(self):
        pass


    '''内存使用率'''
    def memory_usage(self):
        pass


    '''磁盘信息'''
    def disk_info(self):
    
        tmp_list = []

        for physical_disk in self.computer.Win32_DiskDrive(): 

            for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
        
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):

                    tmp_dict = {}
                    tmp_dict['Caption'] = logical_disk.Caption
                    tmp_dict["DiskTotal"] = int(logical_disk.Size) / (1024**3)
                    tmp_dict["UseSpace"] = (int(logical_disk.Size) - int(logical_disk.FreeSpace)) / (1024**3)
                    tmp_dict["FreeSpace"] = int(logical_disk.FreeSpace) / (1024**3)
                    tmp_dict["Percent"] = int(100.0 * (int(logical_disk.Size) - int(logical_disk.FreeSpace)) / int(logical_disk.Size))

                    tmp_list.append(tmp_dict)

        # print(tmp_list)
        return tmp_list


    '''磁盘使用率'''
    def disk_usage(self, disk_name):
    
        for disk in self.disk_info():

            if not disk['Caption'].find(disk_name):

                disk_caption = disk['Caption']     # 磁盘名称
                disk_total = disk['DiskTotal']     # 磁盘大小, 单位为G
                disk_usespace = disk['UseSpace']   # 已用磁盘大小, 单位为G
                disk_freespace = disk['FreeSpace'] # 剩余可用磁盘大小, 单位为G
                disk_usage = disk['Percent']       # 使用率, 单位为%

        # print('磁盘名: {}, 磁盘大小: {} G, 已用空间: {} G, 剩余可用空间: {} G, 使用率为 {}%.'.format(disk_caption.split(':')[0], round(disk_total,2), round(disk_usespace,2), round(disk_freespace,2), disk_usage))
        return disk_caption.split(':')[0], round(disk_total,2), round(disk_usespace,2), round(disk_freespace,2), disk_usage


    '''网络信息'''
    def network_info(self):
        pass                                     