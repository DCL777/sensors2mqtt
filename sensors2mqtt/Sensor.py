#!/usr/bin/python3

#  This file is part of the sensors2mqtt distribution (https://github.com/DCL777/sensors2mqtt.git).
#  Copyright (c) 2020 Dries Claerbout

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3.

#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

import os.path
# from os import path


class BColors:
    """CLI colors"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Sensor:
    """Default sensor class.  Every sensor must be a instance of this class"""

    def __init__(self, supported_system, manufacturer, sensor_name,
                 function, protocol, mqtt_client, parameters):
        self.supported_system = supported_system
        self.manufacturer = manufacturer
        self.sensor_name = sensor_name
        self.function = function
        self.protocol = protocol
        self.mqtt_client = mqtt_client

        self.update_interval = parameters['update_interval']

        # replace spaces and dashes to underscore !!
        sensor_name_modified = self.sensor_name.replace(' ', '_')
        sensor_name_modified = sensor_name_modified.replace('-', '_')

        self.own_dir = f"{os.getcwd()}/sensors/{self.manufacturer}_{sensor_name_modified}/"

        # .get(f"{self.supported_system}_{self.manufacturer}_{sensorNameModified}")
        self.parameters = parameters
        self.logger = logging.getLogger(__name__)

    def print_info(self):
        """ Print info about the used parameters """
        print(f"{BColors.OKCYAN} -> {self.sensor_name} \t {self.manufacturer} \t {self.function} \t {self.protocol} \t {self.supported_system}{BColors.ENDC}")
        #self.count = 0
        # for a_sensor in self.parameters:
        #  self.count = self.count +1
        #print(f"    -> Sensor {self.count}:")
        for an_item in self.parameters.items():
            print(f"        -> {an_item[0]} = {an_item[1]}")
            #print(f"    -> {an_item}")
          #print(f"    -> {a_sensor.items()}")

    def is_configured(self):
        """ is configured? """
        return bool(self.parameters)

    def send_value_over_mqtt(self, mqtt_top_dir_name):
        """ send the actual sensor value over MQTT"""
 #       pass

    def on_exit(self):
        """ Do this on exit """
#        pass

    def get_update_interval(self):
        """ Get the wanted update interval for this sensor """
        return self.update_interval
