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

from Sensor import Sensor


class Maximintegrated_DS18B20(Sensor):
  

  def __init__(self, mqtt_client, config):    
    super().__init__("Maximintegrated", "DS18B20", "Temperature","1-Wire" ,mqtt_client, config)
    
  def read_temp_raw(self,path):
    try:
      sensor_file = open(path, 'r') # Opens the temperature device file
    except (IOError, OSError) as e:
      print(f'\nERROR while opinging file {path}')
      print(f'Sensor not found, check the address or the connection wires')
      print(f'{e}\n')
      return -1000

    raw_data = sensor_file.readlines() # Returns the text
    sensor_file.close()
    sensor_data = raw_data[1].split("t=") # split the second line output at t=
    temp_c = float(sensor_data[1]) / 1000.0 # convert value of t= to calcius
    return temp_c

  def send_value_over_mqtt(self,mqtt_top_dir_name): 
    for sensor in self.parameters:  
      sensor_value = self.read_temp_raw(sensor['path'])  # VALUE: -1000 = ERROR
      mqtt_sub_dir = sensor['mqtt_sub_dir']
      friendly_name = f"{mqtt_top_dir_name}/{mqtt_sub_dir}/{self.function}" #.format(mqtt_sub_dir,self.function)
      self.mqtt_client.publish(friendly_name, sensor_value)
      self.logger.info(f"    MQTT: {friendly_name}  {sensor_value}")    
  
  def activate_100s_action(self):
    pass
  
  def on_exit(self):
    pass