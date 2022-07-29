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

    def __init__(self, mqtt_client, aSensor, mqtt_top_dir_name):
        super().__init__("LINUX", "Sciosense", "CCS811",
                         "TVOC & CO2", "I2C", mqtt_client, aSensor)

        self.mqtt_top_dir_name = mqtt_top_dir_name
        self.mqtt_sub_dir = aSensor['mqtt_sub_dir']
        self.serial_port = aSensor['serial_port']
        self.plantower = plantower.Plantower(port=self.serial_port)
        #print("[LINUX_Plantower_PMS5003] Making sure it's correctly setup for active mode. Please wait")
        # change back into active mode
        self.plantower.mode_change(plantower.PMS_ACTIVE_MODE)
        self.plantower.set_to_wakeup()  # ensure fan is spinning

    def send_value_over_mqtt(self):
        """Send the actual value over mqtt"""
        #print("Start convertion")
        result = self.plantower.read()

        dictData = {}
        dictData['pm10_cf1'] = result.pm10_cf1
        dictData['pm25_cf1'] = result.pm25_cf1
        dictData['pm100_cf1'] = result.pm100_cf1

        dictData['pm10_std'] = result.pm10_std
        dictData['pm25_std'] = result.pm25_std
        dictData['pm100_std'] = result.pm100_std

        dictData['gr03um'] = result.gr03um
        dictData['gr05um'] = result.gr05um
        dictData['gr10um'] = result.gr10um
        dictData['gr25um'] = result.gr25um
        dictData['gr50um'] = result.gr50um
        dictData['gr100um'] = result.gr100um

        all_data_json = json.dumps(dictData)
        friendly_name = f"{self.mqtt_top_dir_name}/{self.mqtt_sub_dir}/{self.function}"
        self.mqtt_client.publish(friendly_name, all_data_json)
        self.logger.info(f"    MQTT: {friendly_name}  {all_data_json}")

    def on_exit(self):
        """ Do this on exit """
        self.plantower.set_to_sleep()
     #   pass
