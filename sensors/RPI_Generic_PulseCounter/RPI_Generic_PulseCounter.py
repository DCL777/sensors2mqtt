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
import RPi.GPIO as GPIO
import logging
import json


import os.path
from os import path

from Sensor import Sensor
from datetime import datetime

class RPI_Generic_PulseCounter(Sensor):
  def __init__(self, mqtt_client, config):    
    super().__init__("RPI","Generic", "PulseCounter", "PulseCounter","GPIO" ,mqtt_client, config)



    self.count_flow_sensor = []
    self.count_flow_sensor_d1 = []
    self.count_flow_sensor_d1_100s = []

    #self.mydir = os.getcwd()

    print(f"TODAY: {datetime.today().day}")
    print(f"WEEK:  {datetime.today().isocalendar()[1]}")
    print(f"MONTH: {datetime.today().month}")
    print(f"YEAR:  {datetime.today().year}")
    print(f"DIR:   {os.getcwd()}")    

    self.path = f"{os.getcwd()}/sensors/{self.__class__.__name__}/{self.__class__.__name__}.txt" 
    print(f"PATH:   {self.path}")


    if path.isfile(self.path):  # check if it exists
      data_file = open(self.path,'r')
      data = data_file.readlines()
      data_file.close()

      i = 0
      for aline in data:
        self.count_flow_sensor.append(int(aline))
        self.count_flow_sensor_d1.append(int(aline))
        self.count_flow_sensor_d1_100s.append(int(aline))
        i = i+1
    else:  # initialize when no file was found to int(0)
      i = 0
      for sensor in self.parameters:
        self.count_flow_sensor.append(int(0))
        self.count_flow_sensor_d1.append(int(0))
        self.count_flow_sensor_d1_100s.append(int(0))
        i = i+1
      data_file = open(self.path,'w+')
      data_file.write("0\n0\n0\n0\n0\n" )
      data_file.close()
    
    self.sensor_pin_lookup = {}  # dict: PIN = location in other tables 0->max

    i = 0
    for sensor in self.parameters: 
      sensor_pin = sensor['pin_number']
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(sensor_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)      
      GPIO.add_event_detect(sensor_pin, GPIO.FALLING, callback=self.countPulse)
      self.sensor_pin_lookup[sensor_pin] = i
      i = i+1


  def countPulse(self,channel):
    id = self.sensor_pin_lookup[channel]
    self.count_flow_sensor[id] = self.count_flow_sensor[id] + 1
    self.logger.debug(f'CHANNEL:  {channel}  \t  {self.count_flow_sensor[id]} ' ) 


  def send_value_over_mqtt(self,mqtt_top_dir_name): 
    id = 0
    for sensor in self.parameters:   
      #if self.count_flow_sensor_d1[id] < self.count_flow_sensor[id]:
      delta = self.count_flow_sensor[id] - self.count_flow_sensor_d1[id]
      self.count_flow_sensor_d1[id] = self.count_flow_sensor[id]  # save last value
      
      mqtt_sub_dir = sensor['mqtt_sub_dir']
      function = sensor['function']
      allData =  dict(delta=f"{delta}", total=f"{self.count_flow_sensor[id]}", day="0", week="0",month="0",year="0")
      allDataJson = json.dumps(allData)

      friendly_name = f"{mqtt_top_dir_name}/{mqtt_sub_dir}/{function}"
      self.mqtt_client.publish(friendly_name, allDataJson)
      self.logger.info(f"    MQTT: {friendly_name}  {allDataJson}")

     #friendly_name = f"{mqtt_top_dir_name}/{mqtt_sub_dir}/{function}/delta" 
     #self.mqtt_client.publish(friendly_name, delta)
     #self.logger.info(f"    MQTT: {friendly_name}  {delta}")
     #friendly_name = f"{mqtt_top_dir_name}/{mqtt_sub_dir}/{function}/total" 
     #self.mqtt_client.publish(friendly_name, self.count_flow_sensor[id])
     #self.logger.info(f"    MQTT: {friendly_name}  {self.count_flow_sensor[id]}")  
      id = id+1                      

 
  def activate_100s_action(self):
    #print("100 seconds => write to file if changed")
    self.save_if_changed()
    return
  
  def save_if_changed(self):
    id = 0
    changed = False
    for sensor in self.parameters: 
      if self.count_flow_sensor_d1_100s[id] < self.count_flow_sensor[id]:       
        changed = True
        self.count_flow_sensor_d1_100s[id] = self.count_flow_sensor[id]
      id = id + 1
    if (bool(changed)):
        data_file = open(self.path,'w+')
        id = 0
        for sensor in self.parameters:
          data_file.write(str(self.count_flow_sensor[id]) + "\n" )
          id = id +1
        data_file.close()
        self.logger.debug (f"save_if_changed => written to file => update found   {self.count_flow_sensor}")   
    else:
      self.logger.debug ("save_if_changed => no changes found")  
    return

  def on_exit(self):
    self.save_if_changed() # save if changed
    GPIO.cleanup()