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

class Sensor:
  def __init__(self, supported_system, manufacturer, sensorName, function,protocol,mqtt_client, parameters):
    self.supported_system = supported_system
    self.manufacturer = manufacturer
    self.sensorName = sensorName
    self.function = function
    self.protocol = protocol
    self.mqtt_client = mqtt_client

    # replace spaces and dashes to underscore !!
    sensorNameModified = self.sensorName.replace(' ', '_')
    sensorNameModified = sensorNameModified.replace('-','_')

    self.parameters = parameters.get(f"{self.supported_system}_{self.manufacturer}_{sensorNameModified}")
    self.logger = logging.getLogger(__name__)


  def printInfo(self):
    print(f" -> {self.sensorName} \t {self.manufacturer} \t {self.function} \t {self.protocol} \t {self.supported_system}")
    self.count = 0
    for a_sensor in self.parameters:
      self.count = self.count +1
      print(f"    -> Sensor {self.count}:")
      for an_item in a_sensor.items():        
        print(f"        -> {an_item[0]} = {an_item[1]}")        
        #print(f"    -> {an_item}")
      #print(f"    -> {a_sensor.items()}")

  def is_configured(self):
    return bool(self.parameters)
  
  def get_sensors_found(self):
    return self.count
  def send_value_over_mqtt(self,mqtt_top_dir_name):
    pass
  def activate_100s_action(self):
    pass
  def on_exit(self):
    pass