#!/usr/bin/python3
 
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


import paho.mqtt.client as mqtt
import paho.mqtt.publish as publishpython
import yaml
import logging
import json
import platform
import psutil

import os.path
from os import path

from Sensor import Sensor
from datetime import datetime

class LINUX_Generic_SystemInfo(Sensor):
  def __init__(self, mqtt_client, sensorParameters,mqtt_top_dir_name):    
    super().__init__("LINUX","Generic", "SystemInfo", "SystemInfo","System Information" ,mqtt_client, sensorParameters)

    self.mqtt_top_dir_name =mqtt_top_dir_name


    self.sensorParameters = sensorParameters
    self.mqtt_client = mqtt_client

    self.send_disk = bool(sensorParameters['send_disk_info'])
    self.send_mem = bool(sensorParameters['send_memory_info'])
    self.send_cpu = bool(sensorParameters['send_cpu_info'])
    self.send_platform = bool(sensorParameters['send_platform_info'])
    self.logger = logging.getLogger(__name__)

 
    my_system = platform.uname() 
    dist = platform.dist()
    dist = " ".join(x for x in dist)

    if self.send_platform:
      self.dictDataStatic =  {}
      self.dictDataStatic['System']  = my_system.system
      self.dictDataStatic['Release'] = my_system.release
      self.dictDataStatic['Version'] = my_system.version
      self.dictDataStatic['Machine'] = my_system.machine
      self.dictDataStatic['Architecture']   = platform.architecture()[0]
      self.dictDataStatic['CPU_Cores']      = psutil.cpu_count(logical=False)
      self.dictDataStatic['Distribution']   = dist
      self.dictDataStatic['Python_Version'] = platform.python_version()
      self.dictDataStatic['Node_Name']      = my_system.node
  
      allDataJson = json.dumps(self.dictDataStatic)
      friendly_name = f"{self.mqtt_top_dir_name}/{self.sensorParameters['mqtt_sub_dir']}/static"
      self.mqtt_client.publish(friendly_name, allDataJson)
      self.logger.info(f"    MQTT: {friendly_name}  {allDataJson}")


  def send_value_over_mqtt(self): 

    uptime = None
    idletime = None
    with open("/proc/uptime", "r") as f:
        data = f.read().split(" ")
        #print(f"data: {data}")
        #datasplitted= data.split(" ")
        #print(f"data Splitted: {datasplitted}")
        uptime = data[0].strip()
        idletime = data[1].strip() 
        
    idletime = (float(idletime) / psutil.cpu_count(logical=False))
    idlepercent = round(100 * float(idletime) / float(uptime),2)   
    idletime = int(idletime)
    uptime = int(float(uptime))

    self.dictDataDynamic =  {}
    self.dictDataDynamic['Uptime']        = uptime
    self.dictDataDynamic['Idle_Time']     = idletime
    self.dictDataDynamic['Idle_Percent']  = idlepercent

    if self.send_cpu:
      self.dictDataDynamic['CPU_Freq']     = psutil.cpu_freq().current
      self.dictDataDynamic['CPU_Percent']  = psutil.cpu_percent()

    if self.send_mem:
      self.dictDataDynamic['MEM_Total']    = psutil.virtual_memory().total
      self.dictDataDynamic['MEM_Used']     = psutil.virtual_memory().available
      self.dictDataDynamic['MEM_Percent']  = psutil.virtual_memory().percent
    
    if self.send_disk:
      self.dictDataDynamic['DISK_Total']    = psutil.disk_usage('/').total
      self.dictDataDynamic['DISK_Used']     = psutil.disk_usage('/').used
      self.dictDataDynamic['DISK_Percent']  = psutil.disk_usage('/').percent

 
    allDataJson = json.dumps(self.dictDataDynamic)
    friendly_name = f"{self.mqtt_top_dir_name}/{self.sensorParameters['mqtt_sub_dir']}/dynamic"
    self.mqtt_client.publish(friendly_name, allDataJson)
    self.logger.info(f"    MQTT: {friendly_name}  {allDataJson}")


  def on_exit(self):
    None