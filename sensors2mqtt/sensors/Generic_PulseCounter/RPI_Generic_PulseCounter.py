#!/usr/bin/python3
'''RPI_Generic_PulseCounter'''
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


#import paho.mqtt.client as mqtt
#import paho.mqtt.publish as publishpython
#import yaml

import logging
import json

from datetime import datetime

import os.path
from os import path

import RPi.GPIO as GPIO

from Sensor import Sensor


class RPI_Generic_PulseCounter(Sensor):
    '''RPI_Generic_PulseCounter'''

    def __init__(self, mqtt_client, sensor_parameters, mqtt_top_dir_name):
        """INIT"""
        super().__init__("RPI", "Generic", "PulseCounter",
                         "PulseCounter", "GPIO", mqtt_client, sensor_parameters)

        self.mqtt_top_dir_name = mqtt_top_dir_name

        #ownDir = f"{os.getcwd()}/sensors/{self.__class__.__name__}/"

        # {self.manufacturer}_{sensorNameModified}
        self.sensor_parameters = sensor_parameters
        self.mqtt_client = mqtt_client

        self.sensor_pin = sensor_parameters['pin_number']
        self.pulse_scale = sensor_parameters['pulse_scale']
        self.counter_scale = sensor_parameters['counter_scale']
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
            self.dict_data = dict(delta=f"0", total=f"0",
                                  day="0", week="0", month="0", year="0")
            self.total_d1 = 0
            self.save_to_file()

        #print(f"loaded data: {self.dict_data}")

        GPIO.setmode(GPIO.BCM)  # SysGPIO better ?????
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.sensor_pin, GPIO.BOTH,
                              callback=self.count_pulse, bouncetime=10)
        self.pin_d1 = GPIO.input(self.sensor_pin)

        # if self.logger.level == logging.DEBUG:
        #  print (f"This module works in DEBUG MODE {self.logger.level}")
        # else:
        #  print (f"This module works in NORMAL MODE {self.logger.level}")

    def count_pulse(self, channel):
        """Count the pulses: increment"""
        if GPIO.input(self.sensor_pin) != self.pin_d1:
            self.dict_data['total'] = float(
                self.dict_data['total']) + self.pulse_scale
        self.pin_d1 = GPIO.input(self.sensor_pin)

        # if GPIO.input(self.sensor_pin):
        #  if self.pin_d1:
        #    print (f"Rising edge detected on {self.sensor_pin}  WRONG EVENT !!!!! " )
        #  else:
        #    print (f"Rising edge detected on {self.sensor_pin} ")
        # else:
        #  if self.pin_d1:
        #    print (f"Falling edge detected on {self.sensor_pin}")
        #  else:
        #    print (f"Falling edge detected on {self.sensor_pin}  WRONG EVENT !!!!! ")
        # self.update_dict_data_scaled()
        #self.logger.debug(f'CHANNEL:  {channel}  \t  {self.dict_dataScaled} ' )

    def update_dict_data_scaled(self):
        """Update dictionary data scaled"""
        self.dict_data['delta'] = float(
            self.dict_data['total']) - float(self.total_d1)
        self.dict_dataScaled = {}
        self.dict_dataScaled['delta'] = round(
            float(self.dict_data['delta']) * self.counter_scale, 1)
        self.dict_dataScaled['total'] = round(
            float(self.dict_data['total']) * self.counter_scale, 1)
        self.dict_dataScaled['day'] = round(
            (float(self.dict_data['total']) - float(self.dict_data['day'])) * self.counter_scale, 1)
        self.dict_dataScaled['week'] = round((float(
            self.dict_data['total']) - float(self.dict_data['week'])) * self.counter_scale, 1)
        self.dict_dataScaled['month'] = round((float(
            self.dict_data['total']) - float(self.dict_data['month'])) * self.counter_scale, 1)
        self.dict_dataScaled['year'] = round((float(
            self.dict_data['total']) - float(self.dict_data['year'])) * self.counter_scale, 1)

    def send_value_over_mqtt(self):
        """Send the actual value over mqtt"""
        # ------------------------------------------------------------------------
        if self.year_d1 != datetime.today().year:
            self.dict_data['year'] = self.dict_data['total']
            self.year_d1 = datetime.today().year
        # ------------------------------------------------------------------------
        if self.month_d1 != datetime.today().month:
            self.dict_data['month'] = self.dict_data['total']
            self.month_d1 = datetime.today().month
        # ------------------------------------------------------------------------
        if self.day_d1 != datetime.today().day:
            self.dict_data['day'] = self.dict_data['total']
            self.day_d1 = datetime.today().day
        # ------------------------------------------------------------------------
        if self.week_d1 != datetime.today().isocalendar()[1]:
            self.dict_data['week'] = self.dict_data['total']
            self.week_d1 = datetime.today().isocalendar()[1]
        # ------------------------------------------------------------------------
        self.update_dict_data_scaled()
        self.total_d1 = self.dict_data['total']  # save last value
        # ------------------------------------------------------------------------

        all_data_json = json.dumps(self.dict_dataScaled)
        friendly_name = f"{self.mqtt_top_dir_name}/{self.sensor_parameters['mqtt_sub_dir']}/{self.sensor_parameters['function']}"
        self.mqtt_client.publish(friendly_name, all_data_json)
        self.logger.info(f"    MQTT: {friendly_name}  {all_data_json}")

        if self.dict_data['delta'] > 0:
            #print("delta > 0 => save to file")
            self.save_to_file()

    def save_to_file(self):
        """Save data to file"""
        with open(self.json_file, "w") as outfile:
            json.dump(self.dict_data, outfile)
            self.logger.debug(f"saved to file  {self.json_file}")

    def read_from_file(self):
        """Read from File"""
        with open(self.json_file) as json_file:
            self.dict_data = json.load(json_file)
            self.dict_data['delta'] = 0  # reset delta
        #print(f"dictData: {self.dict_data}")
        self.total_d1 = self.dict_data['total']

    def on_exit(self):
        """ Do this on exit """
        self.save_to_file()
        GPIO.cleanup()
