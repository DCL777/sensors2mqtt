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

import logging

import os.path
from os import path

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Sensor:
  def __init__(self, supported_system, manufacturer, sensorName, function,protocol,mqtt_client, parameters):
    self.supported_system = supported_system
    self.manufacturer = manufacturer
    self.sensorName = sensorName
    self.function = function
    self.protocol = protocol
    self.mqtt_client = mqtt_client

    self.update_interval = parameters['update_interval']

    # replace spaces and dashes to underscore !!
    sensorNameModified = self.sensorName.replace(' ', '_')
    sensorNameModified = sensorNameModified.replace('-','_')

    self.ownDir = f"{os.getcwd()}/sensors/{self.manufacturer}_{sensorNameModified}/"

    self.parameters = parameters #.get(f"{self.supported_system}_{self.manufacturer}_{sensorNameModified}")
    self.logger = logging.getLogger(__name__)


  def printInfo(self):
    print(f"{BColors.OKCYAN} -> {self.sensorName} \t {self.manufacturer} \t {self.function} \t {self.protocol} \t {self.supported_system}{BColors.ENDC}")
    #self.count = 0
    #for a_sensor in self.parameters:
    #  self.count = self.count +1
    #print(f"    -> Sensor {self.count}:")
    for an_item in self.parameters.items():        
      print(f"        -> {an_item[0]} = {an_item[1]}")        
        #print(f"    -> {an_item}")
      #print(f"    -> {a_sensor.items()}")

  def is_configured(self):
    return bool(self.parameters)
  
  def send_value_over_mqtt(self,mqtt_top_dir_name):
    pass

  def on_exit(self):
    pass

  def get_update_interval(self):
    return self.update_interval