#!/usr/bin/python3
'''LINUX_Maximintegrated_DS18B20'''
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


#import logging

from Sensor import Sensor


class LINUX_Maximintegrated_DS18B20(Sensor):
    """LINUX_Maximintegrated_DS18B20"""
    def __init__(self, mqtt_client, config, mqtt_top_dir_name):
        super().__init__("LINUX", "Maximintegrated", "DS18B20",
                         "Temperature", "1-Wire", mqtt_client, config)
        self.mqtt_top_dir_name = mqtt_top_dir_name

    def read_temp_raw(self, path):
        """Read the raw temerature"""
        try:
            sensor_file = open(path, 'r')  # Opens the temperature device file
        except (IOError, OSError) as e:
            print(f'\nERROR while opinging file {path}')
            print(f'Sensor not found, check the address or the connection wires')
            print(f'{e}\n')
            return -1000

        raw_data = sensor_file.readlines()  # Returns the text
        sensor_file.close()
        # split the second line output at t=
        sensor_data = raw_data[1].split("t=")
        # convert value of t= to calcius
        temp_c = float(sensor_data[1]) / 1000.0
        return temp_c

    def send_value_over_mqtt(self):
        """Send the actual value over mqtt"""
        # for sensor in self.parameters:
        sensor_value = self.read_temp_raw(
            self.parameters['path'])  # VALUE: -1000 = ERROR
        mqtt_sub_dir = self.parameters['mqtt_sub_dir']
        # .format(mqtt_sub_dir,self.function)
        friendly_name = f"{self.mqtt_top_dir_name}/{mqtt_sub_dir}/{self.function}"
        self.mqtt_client.publish(friendly_name, sensor_value)
        self.logger.info(f"    MQTT: {friendly_name}  {sensor_value}")

    def on_exit(self):
        """ Do this on exit """
   #     pass
