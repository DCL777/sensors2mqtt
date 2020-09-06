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


# Import package
import os
import glob
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publishpython
import yaml
import sys
import logging
import importlib
import argparse
import traceback

from Sensor import Sensor


__version__ = "0.0.1"
__date__ = "2020-08-15"
__author__ = "Dries Claerbout"
__license__ = "AGPL-3.0+"
__status__ = "Debug" #"Production"
__name__ = "sensor2MQTT"

class sensors2mqtt():

  def __init__(self, config, logging):
    if config is None:
      self.config = "sensors_settings.yaml"
    else:
      self.config = config
    self.logging = logging

  def loadConfig(self, path):
    with open(path, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return config

  def initMQTT(self,config_mqtt):
    print(f"Start MQTT: Broker: {config_mqtt['broker']} Username: {config_mqtt['username']} \n") #Password: {config_mqtt['password']}")
    
    try:
      client = mqtt.Client()
      client.username_pw_set(config_mqtt['username'], config_mqtt['password'])
      client.connect(config_mqtt['broker'])
      client.loop_start()    
      return client
    except:
      print("Unable to start MQTT Client.  Did you add the correct PASSWORD in your YAML file?\n")
      print("Possible reasons:")
      print("  -> wrong IP ADDRESS in your YAML file")
      print("  -> wrong PASSWORD in your YAML file")
      print("  -> is the MQTT server up and running?\n\n")
      sys.exit()

  def run (self):


    logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
    if self.logging is None:      
      logging.basicConfig(format=logFormatter, level=logging.ERROR)  # change this to  DEBUG, TEST, WARNING or ERROR to see more or less info
    elif self.logging == 'debug':
      logging.basicConfig(format=logFormatter, level=logging.DEBUG)  # change this to  DEBUG, TEST, WARNING or ERROR to see more or less info
    else:
      logging.basicConfig(format=logFormatter, level=logging.ERROR)  # change this to  DEBUG, TEST, WARNING or ERROR to see more or less info
    logger = logging.getLogger(__name__)

  
    print("============================")
    print(f"Start Sensors to MQTT V{__version__}             {__date__} {__author__}")
    print("============================")
  
    config_yaml = self.loadConfig(self.config)
    config_mqtt = config_yaml['mqtt']
    client = self.initMQTT(config_mqtt)
  
    mqtt_top_dir_name = config_mqtt['top_dir_name']
  

    mySensorList = []
    config_sensors = config_yaml['Sensors']

    logger.debug(f"Loading modules:")
    logger.debug(f"================")
    # load only the sensors needed
    for aSensorClass in config_sensors:
      #https://realpython.com/python-import/
      class_to_load = f"sensors.{aSensorClass}.{aSensorClass}"
      module = importlib.import_module(class_to_load)
      logger.debug(f"    --> CLASS: {class_to_load}")
      aClass = getattr(module, f"{aSensorClass}")
      myClass = aClass(client,config_sensors)
      mySensorList.append(myClass)

  
    print("\nSensors found")
    print("----------------------------------------------------------------------")
    for x in mySensorList:
      x.printInfo()
    print("----------------------------------------------------------------------\n\n")

    print("\nStarting main loop...")
    while True:       
      try:

      
        if ((time.time() %100.0 ) < 2):
            logger.debug(f"100 seconds event => write to file if changed {time.time()} =================================")
            for x in mySensorList:
              try:
                x.activate_100s_action()  
              except Exception as e:
                logging.error("\n\n\n" + traceback.format_exc() + "\n" )         
        else:
            logger.debug(f"10 seconds event {time.time()} ----------------------------------------------------------")        
  
     
        for x in mySensorList:
          try:
            x.send_value_over_mqtt(mqtt_top_dir_name)
          except Exception as e:
            logging.error("\n\n\n" + traceback.format_exc() + "\n" )  
  
        time.sleep(10.0 - ((time.time()) % 10.0))
      except KeyboardInterrupt:
        print ('\ncaught keyboard interrupt!, bye')
        for x in mySensorList:
          x.on_exit()
        sys.exit()




parser = argparse.ArgumentParser()
parser.add_argument('-c', dest='config',default="sensors_settings.yaml", help='path to your config file i.e. sensors_settings.yaml (= default value)')
parser.add_argument('-l', dest='logging',default="error", help='debug or error')
args = parser.parse_args()
sens2mqtt = sensors2mqtt(args.config, args.logging)
sens2mqtt.run()
