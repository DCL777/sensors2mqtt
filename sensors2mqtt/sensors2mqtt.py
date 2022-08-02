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

# extra feature: log to file:
# http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/


# Import package
#import os
#import glob
import time
import sys
import logging
import importlib
import argparse
import traceback
import paho.mqtt.client as mqtt
#import paho.mqtt.publish as publishpython
import yaml

#import platform
#from Sensor import Sensor
from Sensor import BColors


__version__ = "0.0.1"
__date__ = "2020-08-15"
__author__ = "Dries Claerbout"
__license__ = "AGPL-3.0+"
__status__ = "Debug"  # "Production"
#__name__ = "sensor2MQTT"


class sensors2mqtt():
    """Sensor2MQTT main class"""

    def __init__(self, config, logging):
        if config is None:
            self.config = "sensors_settings.yaml"
        else:
            self.config = config
        self.logging = logging
        self.my_sensor_list = []

    def load_config(self, path):
        """Load configurataion"""
        with open(path, 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return config

    def init_mqtt(self, config_mqtt):
        """Initialize MQTT"""
        print(
            f"Start MQTT: Broker: {config_mqtt['broker']} Username: {config_mqtt['username']} \n")  # Password: {config_mqtt['password']}")

        try:
            client = mqtt.Client()
            client.username_pw_set(
                config_mqtt['username'], config_mqtt['password'])
            client.connect(config_mqtt['broker'])
            client.loop_start()
            return client
        except:
            print(f"{BColors.FAIL}Unable to start MQTT Client. {BColors.ENDC} Did you add the correct PASSWORD in your YAML file?\n")
            print("Possible reasons:")
            print("  -> wrong IP ADDRESS in your YAML file")
            print("  -> wrong PASSWORD in your YAML file")
            print("  -> is the MQTT server up and running?\n\n")
            sys.exit()

    def send_update(self, event):
        """Send Update"""
        logging.info(f"EVENT = {event}")
        #logging.info("EVENT = %s", event)
        for x in self.my_sensor_list:
            try:
                if int(x.get_update_interval()) <= int(event):
                    x.send_value_over_mqtt()
            except Exception as e:
                logging.error("\n\n\n%s\n" , traceback.format_exc() )

    def run(self):
        """RUN IT"""
        log_formatter = '%(asctime)s - %(levelname)s - %(message)s'
        if self.logging is None:
            # change this to  DEBUG, TEST, WARNING or ERROR to see more or less info
            logging.basicConfig(format=log_formatter, level=logging.ERROR)
        elif self.logging == 'debug':
            # change this to  DEBUG, TEST, WARNING or ERROR to see more or less info
            logging.basicConfig(format=log_formatter, level=logging.DEBUG)
        else:
            # change this to  DEBUG, TEST, WARNING or ERROR to see more or less info
            logging.basicConfig(format=log_formatter, level=logging.ERROR)
        logger = logging.getLogger(__name__)

        print(f"{BColors.HEADER}============================")
        print(
            f"Start Sensors to MQTT V{__version__}             {__date__} {__author__}")
        print(f"============================{BColors.ENDC}")

        config_yaml = self.load_config(self.config)
        config_mqtt = config_yaml['mqtt']
        client = self.init_mqtt(config_mqtt)

        mqtt_top_dir_name = config_mqtt['top_dir_name']

        self.my_sensor_list = []
        config_sensors = config_yaml['Sensors']

        logger.debug("Loading modules:")
        logger.debug("================")

        if config_sensors is None:
            print(
                f"\n{BColors.FAIL}No Sensors configured in the settings-file: {self.config}{BColors.ENDC}")
            print(f"\nNothing to do, so this program will be stopped\n")
            exit()

        # load only the sensors needed
        for a_sensor_class in config_sensors:
            #print(f"a_sensor_class =  {a_sensor_class}")
            sensor_list = config_sensors.get(f"{a_sensor_class}")
            for a_sensor in sensor_list:
                #print(f"a_sensor =  {a_sensor}")
                #print(f"platform =  {a_sensor['platform']}")
                # https://realpython.com/python-import/
                class_to_load = f"sensors.{a_sensor_class}.{a_sensor['platform']}_{a_sensor_class}"
                #print(f"class_to_load =  {class_to_load}")
                module = importlib.import_module(class_to_load)
                logger.debug(f"    --> CLASS: {class_to_load}")
                a_class = getattr(
                    module, f"{a_sensor['platform']}_{a_sensor_class}")
                my_class = a_class(client, a_sensor, mqtt_top_dir_name)
                self.my_sensor_list.append(my_class)

        lowest_update_interval = 43200  # = 12h

        print("\nSensors found")
        print("----------------------------------------------------------------------")
        for x in self.my_sensor_list:
            x.print_info()
            if x.get_update_interval() < lowest_update_interval:
                lowest_update_interval = x.get_update_interval()
            print(
                "----------------------------------------------------------------------")
        print(f"Lowest Update Interval: {lowest_update_interval} seconds")

        print("\n\n\nStarting main loop...")
        self.send_update(43200)
        time.sleep(int(10) - ((time.time()) % float(10)))

        while True:
            try:
                event = 43200
# seconds  10,30,60, 300 (5min) , 900 (15min), 3600 (1h) , 10800 (3h), 21600 (6h) , 43200 (12h)
                if (time.time() % 43200.0) < 2:
                    event = 43200
                elif (time.time() % 21600.0) < 2:
                    event = 21600
                elif (time.time() % 10800.0) < 2:
                    event = 10800
                elif (time.time() % 3600.0) < 2:
                    event = 3600
                elif (time.time() % 900.0) < 2:
                    event = 900
                elif (time.time() % 300) < 2:
                    event = 300
                elif (time.time() % 60) < 2:
                    event = 60
                elif (time.time() % 30) < 2:
                    event = 30
                elif (time.time() % 10) < 2:
                    event = 10
                # else:
                #  logging.error("\n  ===========> event not in range (!) check" )

                self.send_update(event)

                time.sleep(int(lowest_update_interval) -
                           ((time.time()) % float(lowest_update_interval)))
            except KeyboardInterrupt:
                print('\ncaught keyboard interrupt!, bye')
                for x in self.my_sensor_list:
                    x.on_exit()
                sys.exit()


parser = argparse.ArgumentParser()
parser.add_argument('-c', dest='config', default="sensors_settings.yaml", help='path to your config file i.e. sensors_settings.yaml (= default value)')
parser.add_argument('-l', dest='logging', default="error", help='debug or error')
args = parser.parse_args()
sens2mqtt = sensors2mqtt(args.config, args.logging)
sens2mqtt.run()
