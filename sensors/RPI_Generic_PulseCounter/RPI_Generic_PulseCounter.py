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

class one_Generic_PulsCounter():

  def __init__(self, mqtt_client, sensorParameters,ownDir): 
    self.sensorParameters = sensorParameters
    self.mqtt_client = mqtt_client

    self.sensor_pin = sensorParameters['pin_number']
    self.scaleFactor = sensorParameters['scale_factor']
    self.logger = logging.getLogger(__name__)

    #print(f"TODAY: {datetime.today().day}")
    #print(f"WEEK:  {datetime.today().isocalendar()[1]}")
    #print(f"MONTH: {datetime.today().month}")
    #print(f"YEAR:  {datetime.today().year}")
    #print(f"DIR:   {os.getcwd()}")    

    self.day_d1 = datetime.today().day
    self.week_d1 = datetime.today().isocalendar()[1]
    self.month_d1 = datetime.today().month
    self.year_d1 = datetime.today().year

    self.json_file = f"{ownDir}pin_{self.sensor_pin}.json"     
    #print(f"json_file:   {self.json_file}")

    if path.isfile(self.json_file):  # check if it exists
      self.read_from_file()
    else:  # initialize when no file was found to int(0)
      self.dictData = dict(delta=f"0", total=f"0", day="0", week="0",month="0",year="0")
      self.total_d1 = 0
      self.save_to_file()

    print(f"loaded data: {self.dictData}")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)      
    GPIO.add_event_detect(self.sensor_pin, GPIO.FALLING, callback=self.countPulse)


  def countPulse(self,channel):    
    self.dictData['total'] = int(self.dictData['total']) + 1
    self.logger.debug(f'CHANNEL:  {channel}  \t  {self.dictData} ' ) 

  def send_value_over_mqtt(self,mqtt_top_dir_name): 

      self.dictData['delta'] = int(self.dictData['total']) - int(self.total_d1)
      self.total_d1 = self.dictData['total']  # save last value

      #------------------------------------------------------------------------
      if self.day_d1 != datetime.today().day:
        self.dictData['day'] = self.dictData['delta'] # start new day
        self.day_d1 = datetime.today().day
      else:
        self.dictData['day'] = int(self.dictData['day']) + int(self.dictData['delta'])
      #------------------------------------------------------------------------
      if self.week_d1 != datetime.today().isocalendar()[1]:
        self.dictData['week'] = self.dictData['delta'] # start new week
        self.week_d1 = datetime.today().isocalendar()[1]
      else:
        self.dictData['week'] = int(self.dictData['week']) + int(self.dictData['delta'])
      #------------------------------------------------------------------------
      if self.month_d1 != datetime.today().month: 
        self.dictData['month'] = self.dictData['delta'] # start new month
        self.month_d1 = datetime.today().month
      else:
        self.dictData['month'] = int(self.dictData['month']) + int(self.dictData['delta'])
      #------------------------------------------------------------------------
      if self.year_d1 != datetime.today().year:
        self.dictData['year'] = self.dictData['delta'] # start new year
        self.year_d1 = datetime.today().year
      else:
        self.dictData['year'] = int(self.dictData['year']) + int(self.dictData['delta'])
      #------------------------------------------------------------------------
      
      self.dictDataScaled =  {}
      for key in self.dictData:
        self.dictDataScaled[key] = int(self.dictData[key]) * self.scaleFactor


      allDataJson = json.dumps(self.dictDataScaled)
      friendly_name = f"{mqtt_top_dir_name}/{self.sensorParameters['mqtt_sub_dir']}/{self.sensorParameters['function']}"
      self.mqtt_client.publish(friendly_name, allDataJson)
      self.logger.info(f"    MQTT: {friendly_name}  {allDataJson}")

      if self.dictData['delta'] > 0:
        self.save_to_file
        


  def save_to_file(self):
    with open(self.json_file, "w") as outfile:  
      json.dump(self.dictData, outfile)
      self.logger.debug (f"saved to file  {self.json_file}")


  def read_from_file(self):
      with open(self.json_file) as json_file: 
        self.dictData = json.load(json_file) 
      #print(f"dictData: {self.dictData}")
      self.total_d1 = self.dictData['total']




class RPI_Generic_PulseCounter(Sensor):
  def __init__(self, mqtt_client, config):    
    super().__init__("RPI","Generic", "PulseCounter", "PulseCounter","GPIO" ,mqtt_client, config)
    self.mySensorList = []
    for sensor in self.parameters: 
      self.mySensorList.append(one_Generic_PulsCounter(mqtt_client,sensor,f"{os.getcwd()}/sensors/{self.__class__.__name__}/") )


  def send_value_over_mqtt(self,mqtt_top_dir_name): 
    for x in self.mySensorList:
      x.send_value_over_mqtt(mqtt_top_dir_name)
 
  def activate_100s_action(self):
    #print("100 seconds => write to file if changed")
    #self.save_to_file()
    return
  
  def on_exit(self):
    for x in self.mySensorList:
      x.save_to_file() 
    GPIO.cleanup()