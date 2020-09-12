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
  def __init__(self, mqtt_client, sensorParameters,mqtt_top_dir_name):    
    super().__init__("RPI","Generic", "PulseCounter", "PulseCounter","GPIO" ,mqtt_client, sensorParameters)

    self.mqtt_top_dir_name =mqtt_top_dir_name

    #ownDir = f"{os.getcwd()}/sensors/{self.__class__.__name__}/"
    
    #{self.manufacturer}_{sensorNameModified}
    self.sensorParameters = sensorParameters
    self.mqtt_client = mqtt_client

    self.sensor_pin = sensorParameters['pin_number']
    self.pulseScale = sensorParameters['pulse_scale']
    self.counterScale = sensorParameters['counter_scale']
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

    self.json_file = f"{self.ownDir}pin_{self.sensor_pin}.json"     
    #print(f"json_file:   {self.json_file}")

    if path.isfile(self.json_file):  # check if it exists
      self.read_from_file()
    else:  # initialize when no file was found to int(0)
      self.dictData = dict(delta=f"0", total=f"0", day="0",month="0",year="0", all="0")
      self.total_d1 = 0
      self.save_to_file()

    #print(f"loaded data: {self.dictData}")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)      
    GPIO.add_event_detect(self.sensor_pin, GPIO.FALLING, callback=self.countPulse)


  def countPulse(self,channel):    
    self.dictData['total'] = float(self.dictData['total']) + self.pulseScale
    self.logger.debug(f'CHANNEL:  {channel}  \t  {self.dictData} ' ) 

  def send_value_over_mqtt(self): 

      self.dictData['delta'] = float(self.dictData['total']) - float(self.total_d1)
      self.total_d1 = self.dictData['total']  # save last value

      # day     delta_steps_one_day   = one day increments with  delta
      # month   day_steps_one_month   = one week increments with total day 
      # removed # year wsoy  week_steps_one_year   = one month increments with total day
      # year    month_steps_one_year  = one year increments with a total month value
      # all     year_steps            = one year increments with a total month value
        
      #------------------------------------------------------------------------
      if self.year_d1 != datetime.today().year:
        self.dictData['all'] = float(self.dictData['all']) + float(self.dictData['year'])
        self.dictData['year'] = self.dictData['month'] # start new month
        self.month_d1 = datetime.today().month
      else:
        if self.month_d1 != datetime.today().month: 
          self.dictData['year'] = float(self.dictData['year']) + float(self.dictData['month'])
      #------------------------------------------------------------------------
      if self.month_d1 != datetime.today().month: 
        self.dictData['month'] = self.dictData['day'] # start new day
        self.day_d1 = datetime.today().day
      else:
        if self.day_d1 != datetime.today().day:
          self.dictData['month'] = float(self.dictData['month']) + float(self.dictData['day'])
      #------------------------------------------------------------------------
      if self.day_d1 != datetime.today().day:
        self.dictData['day'] = self.dictData['delta']  # start new day
        self.day_d1 = datetime.today().day
      else:
        self.dictData['day'] = float(self.dictData['day']) + float(int(self.dictData['delta'] ))
      #------------------------------------------------------------------------
      #if self.week_d1 != datetime.today().isocalendar()[1]:
      #  self.dictData['owi'] = self.dictData['delta'] # start new week
      #  self.week_d1 = datetime.today().isocalendar()[1]
      #else:
      #  self.dictData['owi'] = int(self.dictData['owi']) + int(self.dictData['delta'])
      #------------------------------------------------------------------------


      
      self.dictDataScaled =  {}
      for key in self.dictData:
        self.dictDataScaled[key] = round(float(self.dictData[key]) * self.counterScale,1)


      allDataJson = json.dumps(self.dictDataScaled)
      friendly_name = f"{self.mqtt_top_dir_name}/{self.sensorParameters['mqtt_sub_dir']}/{self.sensorParameters['function']}"
      self.mqtt_client.publish(friendly_name, allDataJson)
      self.logger.info(f"    MQTT: {friendly_name}  {allDataJson}")

      if self.dictData['delta'] > 0:
        #print("delta > 0 => save to file")
        self.save_to_file()
        


  def save_to_file(self):
    with open(self.json_file, "w") as outfile:  
      json.dump(self.dictData, outfile)
      self.logger.debug (f"saved to file  {self.json_file}")


  def read_from_file(self):
      with open(self.json_file) as json_file: 
        self.dictData = json.load(json_file) 
      #print(f"dictData: {self.dictData}")
      self.total_d1 = self.dictData['total']

 
  def activate_100s_action(self):
    #print("100 seconds => write to file if changed")
    #self.save_to_file()
    return
  
  def on_exit(self):
    self.save_to_file() 
    GPIO.cleanup()