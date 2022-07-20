#!/usr/bin/python3
 
#  This file is part of the sensors2mqtt distribution (https://github.com/DCL777/sensors2mqtt.git).
#  Copyright (c) 2021 Dries Claerbout 
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
import time
import json
import plantower

from datetime import datetime
from Sensor import Sensor


# https://github.com/FEEprojects/plantower/blob/master/plantower/plantower.py

class LINUX_Plantower_PMS5003(Sensor):
  

  def __init__(self, mqtt_client, aSensor,mqtt_top_dir_name):    
    super().__init__("LINUX","Sciosense", "CCS811", "TVOC & CO2","I2C" ,mqtt_client, aSensor)

    self.mqtt_top_dir_name = mqtt_top_dir_name
    self.mqtt_sub_dir         = aSensor['mqtt_sub_dir']     
    self.serial_port          = aSensor['serial_port']
    self.PLANTOWER = plantower.Plantower(port=self.serial_port)
    #print("[LINUX_Plantower_PMS5003] Making sure it's correctly setup for active mode. Please wait")
    self.PLANTOWER.mode_change(plantower.PMS_ACTIVE_MODE) #change back into active mode
    self.PLANTOWER.set_to_wakeup() #ensure fan is spinning



  def send_value_over_mqtt(self): 
    #print("Start convertion")
    RESULT = self.PLANTOWER.read()

    dictData =  {}
    dictData['pm10_cf1']  = RESULT.pm10_cf1
    dictData['pm25_cf1']  = RESULT.pm25_cf1
    dictData['pm100_cf1'] = RESULT.pm100_cf1

    dictData['pm10_std']  = RESULT.pm10_std
    dictData['pm25_std']  = RESULT.pm25_std
    dictData['pm100_std'] = RESULT.pm100_std

    dictData['gr03um']    = RESULT.gr03um
    dictData['gr05um']    = RESULT.gr05um
    dictData['gr10um']    = RESULT.gr10um
    dictData['gr25um']    = RESULT.gr25um
    dictData['gr50um']    = RESULT.gr50um
    dictData['gr100um']   = RESULT.gr100um

    allDataJson = json.dumps(dictData)
    friendly_name = f"{self.mqtt_top_dir_name}/{self.mqtt_sub_dir}/{self.function}"
    self.mqtt_client.publish(friendly_name, allDataJson)
    self.logger.info(f"    MQTT: {friendly_name}  {allDataJson}")
  
  def on_exit(self):
    self.PLANTOWER.set_to_sleep()
    pass

