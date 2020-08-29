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

  def __init__(self, config):
    if config is None:
      self.config = "sensors.yaml"
    else:
      self.config = config
    print (f'config 2 = {config}')

  def loadConfig(self, path):
    with open(path, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return config

  def initMQTT(self,config_mqtt):
    print(f"Start MQTT: Broker: {config_mqtt['broker']} Username: {config_mqtt['username']} ") #Password: {config_mqtt['password']}")
    client = mqtt.Client()
    client.username_pw_set(config_mqtt['username'], config_mqtt['password'])
    client.connect(config_mqtt['broker'])
    client.loop_start()    
    return client

  def run (self):

    logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormatter, level=logging.ERROR)
    logger = logging.getLogger(__name__)
  #  logger.debug("debug")
  #  logger.info("test")
  #  logger.warning("warning")
  #  logger.error("error")
  #  logger.critical("critical")
  
    print("============================")
    print(f"\nStart Sensors to MQTT V{__version__}             {__date__} {__author__}")
    print("============================")
  
    config_yaml = self.loadConfig(self.config)
    config_mqtt = config_yaml['mqtt']
    client = self.initMQTT(config_mqtt)
  
    mqtt_top_dir_name = config_mqtt['top_dir_name']
  

    mySensorList = []
    config_sensors = config_yaml['Sensors']

    # load only the sensors needed
    for aSensorClass in config_sensors:
      #print(f"{aSensorClass}")
      #https://realpython.com/python-import/
      module = importlib.import_module(f"sensors.{aSensorClass}")
      aClass = getattr(module, f"{aSensorClass}")
      myClass = aClass(client,config_sensors)
      mySensorList.append(myClass)

  
    print("\nSensors found")
    print("----------------------------------------------------------------------")
    for x in mySensorList:
      x.printInfo()
      #print(f" -> {x.printInfo()} \t configured: {x.is_configured()}")  
    print("----------------------------------------------------------------------\n\n")

    logger.debug("\nStarting main loop...")
    while True:       
      try:
        #      send_mqtt_temperature_values(client, config_yaml['sensors-temperature'])
  
      
      
        if ((time.time() %100.0 ) < 2):
            logger.debug(f"100 seconds event => write to file if changed {time.time()}")
            for x in mySensorList:
              try:
                x.activate_100s_action()  
              except Exception as e:
                logging.error("\n\n\n" + traceback.format_exc() + "\n" )         
        else:
            logger.debug(f"10 seconds event {time.time()}")        
  
     
        for x in mySensorList:
          try:
            x.send_value_over_mqtt(mqtt_top_dir_name)
          except Exception as e:
            logging.error("\n\n\n" + traceback.format_exc() + "\n" )  

     
            
        #send_mqtt_temperature_values(client, config_yaml['sensors-temperature'])
  
        time.sleep(10.0 - ((time.time()) % 10.0))
      except KeyboardInterrupt:
        print ('\ncaught keyboard interrupt!, bye')
        for x in mySensorList:
          x.on_exit()
        sys.exit()




parser = argparse.ArgumentParser()
parser.add_argument('-c', dest='config',default="sensors.yaml", help='path to your config file i.e. sensors.yaml (= default value)')
args = parser.parse_args()
print (f'config 1 = {args.config}')
sens2mqtt = sensors2mqtt(args.config)
sens2mqtt.run()




#@click.command()
#"@click.option('--config', '-c', help='path to your config file i.e. sensors.yml (= default value)')
#def main(config):
#  print ('config 1 = {config}')
#  sens2mqtt = Sensors_to_MQTT(config)
#  sens2mqtt.run()
