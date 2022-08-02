#!/usr/bin/python3
'''LINUX_TexasInstruments_INA226_4_20mA'''
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


import time
import json

from datetime import datetime
from smbus2 import SMBus, i2c_msg  # https://pypi.org/project/smbus2/


# search for i2c bus:  ls /dev/*i2c*   => /dev/i2c-1  => bus 1
# show devices: i2cdetect -y 1
# source:  https://www.ti.com/lit/ds/symlink/ina219.pdf

from ..TexasInstruments_INA219_4_20mA.LINUX_TexasInstruments_INAGeneric import LINUX_TexasInstruments_INAGeneric

#  ------------------
#  Resistor  = 10 ohm  full range 4-32 mA  => Sensors: 4-20mA fully supported
#  ------------------
#  Current I  Volts value  number height  power disipation
#   4.0 mA	  40 mV	 512  	0	      0	     0.16 mW
#  10.0 mA	100 mV	1280	  768	    1875	 1.00 mW
#  12.8 mA	128 mV	1638.4	1126.4	2750	 1.64 mW
#  20.0 mA	200 mV	2560	  2048	  5000	 4.00 mW
#  32.0 mA	320 mV	4096	  3584	  8750	10.24 mW
#  example: Water height sensor 4-20mA = 0-5000mm => 1 step value = 2.44mm, with oversampling /8 = 0.305mm

#  ------------------
#  Resistor  = 16 ohm  full range 4-20 mA  => Sensors: 4-20mA fully supported
#  ------------------
#  Current I  Volts value  number height  power disipation
#  4.0 mA	   64 mV	819.2	 0	    0	      0.26 mW
#  10.0 mA	160 mV	2048	 1228.8	1875	  1.60 mW
#  12.8 mA	205 mV	2621	 1802.2	2750	  2.62 mW
#  20.0 mA	320 mV	4096	 3276.8	5000	  6.40 mW
#  example: Water height sensor 4-20mA = 0-5000mm => 1 step value = 1.53mm, with oversampling /8 = 0.191mm

#  ------------------
#  Resistor  = 25 ohm  full range 4-12.8 mA  => 50% off max. value supported of 4-20mA
#  ------------------
#  Current I  Volts value  number height  power disipation
#   4.0 mA	100 mV	1280 	 0	    0	    0.40 mW
#  10.0 mA	250 mV	3200	 1920	  1875	2.50 mW
#  12.8 mA	320 mV	4096	 2816	  2750	4.10 mW
#  example: Water height sensor 4-20mA = 0-5000mm => 1 step value = 0.98mm, with oversampling /8 = 0.122mm => max. height 2750mm


#from . LINUX_TexasInstruments_INAGeneric import LINUX_TexasInstruments_INAGeneric


class LINUX_TexasInstruments_INA226_4_20mA(LINUX_TexasInstruments_INAGeneric):
    """LINUX_TexasInstruments_INA226_4_20mA"""
    REG_CONFIG_VALUE_RUN = [
        LINUX_TexasInstruments_INAGeneric.REG_CONFIG, 0x4E, 0x39]
    REG_CONFIG_VALUE_POWER_DOWN = [
        LINUX_TexasInstruments_INAGeneric.REG_CONFIG, 0x4E, 0x38]

    def __init__(self, mqtt_client, a_sensor, mqtt_top_dir_name):
        super().__init__("LINUX", "TexasInstruments",
                         "INA226 4-20mA", "Current", "I2C", mqtt_client, a_sensor, mqtt_top_dir_name)

        self.dictData = dict(value="0", day_delta="0")
        # ---------------------------------------------------
        self.bus = SMBus(self.i2c_channel)
        write = i2c_msg.write(
            self.i2c_address, self.REG_CONFIG_VALUE_POWER_DOWN)
        self.bus.i2c_rdwr(write)
        # self.read_i2c_all_registers()  # See all registers from the INA219 chipset

        self.bus.close()
        # ---------------------------------------------------

    def convert_voltage_data_to_unit(self, data):
        """Convert Voltage to unit"""
        val = int.from_bytes(data, byteorder='big')
        val_mv = val  # TODO BUS Voltage
        return val_mv

    def convert_data_to_mV(self, data):
        """Convert data to mV"""
        val = int.from_bytes(data, byteorder='big')
        val_mv = val * 2.44140625 / 1000  # 80mV / 2**15 (32768) = 2.44140625µV
        return val_mv

    def send_value_over_mqtt(self):
        """Send the actual value over mqtt"""
        #print("Start convertion")

        # ------------------------------------------------------------------------------
        self.bus = SMBus(self.i2c_channel)
        write = i2c_msg.write(self.i2c_address, self.REG_CONFIG_VALUE_RUN)
        self.bus.i2c_rdwr(write)
        # convertion time +/- 8.5 seconds, due to 1024x oversampling
        time.sleep(9)
        # ------------------------------------------------------------------------------
        read = self.read_i2c_value(self.REG_SHUNT_VOLTAGE)
        self.print_value(self.REG_SHUNT_VOLTAGE, read)
        self.dictData['value'] = self.convert_current_data_to_unit(read)
        # ------------------------------------------------------------------------------
        #read = self.read_i2c_value(REG_BUS_VOLTAGE)
        # self.print_value(REG_BUS_VOLTAGE,read)
        #self.dictData['bus_voltage']  = self.convert_voltage_data_to_unit(read)
        # ------------------------------------------------------------------------------
        if self.first_read_after_startup:
            self.first_read_after_startup = False
            self.value_day_d1 = self.dictData['value']
            self.day_d1 = datetime.today().day
            self.dictData['day_delta'] = 0
        elif self.day_d1 != datetime.today().day:
            self.dictData['day_delta'] = self.dictData['value'] - \
                self.value_day_d1  # start new day
            self.value_day_d1 = self.dictData['value']
            self.day_d1 = datetime.today().day
        # ------------------------------------------------------------------------------
        all_data_json = json.dumps(self.dictData)
        mqtt_dir = f"{self.mqtt_top_dir_name}/{self.mqtt_sub_dir}/{self.mqtt_function_name}"
        self.mqtt_client.publish(mqtt_dir, all_data_json)
        self.logger.info(f"    MQTT: {mqtt_dir}  {all_data_json}")
        # ------------------------------------------------------------------------------
        # self.read_i2c_all_registers()
        write = i2c_msg.write(
            self.i2c_address, self.REG_CONFIG_VALUE_POWER_DOWN)
        self.bus.i2c_rdwr(write)
        self.bus.close()

    def activate_100s_action(self):
        """Activate 100s action"""
      #  pass
