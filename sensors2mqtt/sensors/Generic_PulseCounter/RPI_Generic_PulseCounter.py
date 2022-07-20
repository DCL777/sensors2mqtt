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
      self.dictData = dict(delta=f"0", total=f"0", day="0",week="0",month="0",year="0")
      self.total_d1 = 0
      self.save_to_file()

    #print(f"loaded data: {self.dictData}")

    GPIO.setmode(GPIO.BCM)  # SysGPIO better ?????
    GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)      
    GPIO.add_event_detect(self.sensor_pin, GPIO.BOTH, callback=self.countPulse, bouncetime=10)
    self.pin_d1 = GPIO.input(self.sensor_pin)

    #if self.logger.level == logging.DEBUG: 
    #  print (f"This module works in DEBUG MODE {self.logger.level}")
    #else:
    #  print (f"This module works in NORMAL MODE {self.logger.level}")


  def countPulse(self,channel):        

    if GPIO.input(self.sensor_pin) != self.pin_d1: 
      self.dictData['total'] = float(self.dictData['total']) + self.pulseScale
    self.pin_d1 = GPIO.input(self.sensor_pin)

    #if GPIO.input(self.sensor_pin):     
    #  if self.pin_d1:
    #    print (f"Rising edge detected on {self.sensor_pin}  WRONG EVENT !!!!! " )
    #  else:
    #    print (f"Rising edge detected on {self.sensor_pin} ") 
    #else:                  
    #  if self.pin_d1:
    #    print (f"Falling edge detected on {self.sensor_pin}") 
    #  else:
    #    print (f"Falling edge detected on {self.sensor_pin}  WRONG EVENT !!!!! ")    
    #self.updateDictDataScaled()
    #self.logger.debug(f'CHANNEL:  {channel}  \t  {self.dictDataScaled} ' ) 

  def updateDictDataScaled(self):
      self.dictData['delta'] = float(self.dictData['total']) - float(self.total_d1)
      self.dictDataScaled =  {}
      self.dictDataScaled['delta'] = round(float(self.dictData['delta']) * self.counterScale,1)
      self.dictDataScaled['total'] = round(float(self.dictData['total']) * self.counterScale,1)
      self.dictDataScaled['day']   = round((float(self.dictData['total']) - float(self.dictData['day']))   * self.counterScale,1)
      self.dictDataScaled['week']  = round((float(self.dictData['total']) - float(self.dictData['week']))  * self.counterScale,1)
      self.dictDataScaled['month'] = round((float(self.dictData['total']) - float(self.dictData['month'])) * self.counterScale,1)
      self.dictDataScaled['year']  = round((float(self.dictData['total']) - float(self.dictData['year']))  * self.counterScale,1)

  def send_value_over_mqtt(self): 
        
      #------------------------------------------------------------------------
      if self.year_d1 != datetime.today().year:
        self.dictData['year'] = self.dictData['total'] 
        self.year_d1 = datetime.today().year
      #------------------------------------------------------------------------
      if self.month_d1 != datetime.today().month: 
        self.dictData['month'] = self.dictData['total'] 
        self.month_d1 = datetime.today().month
      #------------------------------------------------------------------------
      if self.day_d1 != datetime.today().day:
        self.dictData['day'] = self.dictData['total'] 
        self.day_d1 = datetime.today().day
      #------------------------------------------------------------------------
      if self.week_d1 != datetime.today().isocalendar()[1]:
        self.dictData['week'] = self.dictData['total'] 
        self.week_d1 = datetime.today().isocalendar()[1]
      #------------------------------------------------------------------------    
      self.updateDictDataScaled()
      self.total_d1 = self.dictData['total']  # save last value
      #------------------------------------------------------------------------ 

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
        self.dictData['delta'] = 0  # reset delta
      #print(f"dictData: {self.dictData}")
      self.total_d1 = self.dictData['total']

 
  
  def on_exit(self):
    self.save_to_file() 
    GPIO.cleanup()