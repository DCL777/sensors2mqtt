#!/usr/bin/python
"""LINUX Generic SystemInfo"""
#  This file is part of the sensors2mqtt distribution (https://github.com/DCL777/sensors2mqtt.git).
#  Copyright (c) 2020 Dries Claerbout
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


#import paho.mqtt.client as mqtt
#import paho.mqtt.publish as publishpython
#import yaml
import logging
import json
import platform

#import os.path
from os import path
from datetime import datetime

import psutil
import distro

from Sensor import Sensor


class LINUX_Generic_SystemInfo(Sensor):
    """LINUX Generic SystemInfo"""

    def __init__(self, mqtt_client, sensor_parameters, mqtt_top_dir_name):
        super().__init__("LINUX", "Generic", "SystemInfo", "SystemInfo",
                         "System Information", mqtt_client, sensor_parameters)

        self.mqtt_top_dir_name = mqtt_top_dir_name

        self.sensor_parameters = sensor_parameters
        self.mqtt_client = mqtt_client

        self.send_disk = bool(sensor_parameters['send_disk_info'])
        self.send_mem = bool(sensor_parameters['send_memory_info'])
        self.send_cpu = bool(sensor_parameters['send_cpu_info'])
        self.send_platform = bool(sensor_parameters['send_platform_info'])
        self.logger = logging.getLogger(__name__)
        self.dict_data_dynamic = {}

        my_system = platform.uname()
    #  dist = platform.dist()  # platform.dist removed in Python 3.8
    #  dist = distro.like()
        dist = distro.linux_distribution()
        dist = " ".join(x for x in dist)

        if self.send_platform:
            self.dict_data_static = {}
            self.dict_data_static['System'] = my_system.system
            self.dict_data_static['Release'] = my_system.release
            self.dict_data_static['Version'] = my_system.version
            self.dict_data_static['Machine'] = my_system.machine
            self.dict_data_static['Architecture'] = platform.architecture()[0]
            self.dict_data_static['CPU_Cores'] = psutil.cpu_count(
                logical=False)
            self.dict_data_static['Distribution'] = dist
            self.dict_data_static['Python_Version'] = platform.python_version()
            self.dict_data_static['Node_Name'] = my_system.node

    def send_static_data_over_mqtt(self):
        """Send static data over MQTT"""
        if self.send_platform:
            all_data_json = json.dumps(self.dict_data_static)
            friendly_name = f"{self.mqtt_top_dir_name}/{self.sensor_parameters['mqtt_sub_dir']}/static"
            self.mqtt_client.publish(friendly_name, all_data_json)
            self.logger.info(f"    MQTT: {friendly_name}  {all_data_json}")

    def send_value_over_mqtt(self):
        """Send the actual value over mqtt"""

        uptime = None
        idletime = None
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            data = f.read().split(" ")
            #print(f"data: {data}")
            #datasplitted= data.split(" ")
            #print(f"data Splitted: {datasplitted}")
            uptime = data[0].strip()
            idletime = data[1].strip()

        idletime = (float(idletime) / psutil.cpu_count(logical=False))
        idlepercent = round(100 * float(idletime) / float(uptime), 2)
        idletime = int(idletime)
        uptime = int(float(uptime))

        self.dict_data_dynamic = {}
        self.dict_data_dynamic['Uptime'] = uptime
        self.dict_data_dynamic['Idle_Time'] = idletime
        self.dict_data_dynamic['Idle_Percent'] = idlepercent

        if self.send_cpu:
            self.dict_data_dynamic['CPU_Freq'] = psutil.cpu_freq().current
            self.dict_data_dynamic['CPU_Percent'] = psutil.cpu_percent()

        if self.send_mem:
            self.dict_data_dynamic['MEM_Total'] = psutil.virtual_memory().total
            self.dict_data_dynamic['MEM_Used'] = psutil.virtual_memory(
            ).available
            self.dict_data_dynamic['MEM_Percent'] = psutil.virtual_memory(
            ).percent

        if self.send_disk:
            self.dict_data_dynamic['DISK_Total'] = psutil.disk_usage('/').total
            self.dict_data_dynamic['DISK_Used'] = psutil.disk_usage('/').used
            self.dict_data_dynamic['DISK_Percent'] = psutil.disk_usage(
                '/').percent

        all_data_json = json.dumps(self.dict_data_dynamic)
        friendly_name = f"{self.mqtt_top_dir_name}/{self.sensor_parameters['mqtt_sub_dir']}/dynamic"
        self.mqtt_client.publish(friendly_name, all_data_json)
        self.logger.info(f"    MQTT: {friendly_name}  {all_data_json}")

        self.send_static_data_over_mqtt()

    def on_exit(self):
        """ Do this on exit """
#        None
