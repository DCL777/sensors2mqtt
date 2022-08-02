#!/usr/bin/python3
'''LINUX_TexasInstruments_INAGeneric'''
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


import logging

from datetime import datetime
from abc import abstractmethod

#from smbus2 import SMBus, i2c_msg  # https://pypi.org/project/smbus2/

# search for i2c bus:  ls /dev/*i2c*   => /dev/i2c-1  => bus 1
# show devices: i2cdetect -y 1
# source:  https://www.ti.com/lit/ds/symlink/ina219.pdf


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


from Sensor import Sensor


class LINUX_TexasInstruments_INAGeneric(Sensor):
    '''LINUX TI INA Generic'''

    REG_CONFIG = 0x00
    REG_SHUNT_VOLTAGE = 0x01
    REG_BUS_VOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05

    def __init__(self, supported_system, manufacturer, sensor_name,
                 function, protocol, mqtt_client, parameters, mqtt_top_dir_name):
        super().__init__(supported_system, manufacturer,
                         sensor_name, function, protocol, mqtt_client, parameters)

        self.mqtt_top_dir_name = mqtt_top_dir_name
        self.mqtt_sub_dir = parameters['mqtt_sub_dir']
        self.i2c_channel = parameters['channel']  # "/dev/i2c-1"  = 1
        self.i2c_address = parameters['address']
        self.calibration_low_mA = parameters['calibration_low_mA']
        self.calibration_high_mA = parameters['calibration_high_mA']
        self.full_range_value = parameters['full_range_value']
        self.unit = parameters['unit']
        self.mqtt_function_name = parameters['mqtt_function_name']
        self.shunt = parameters['shunt_resistor']
        self.offset = parameters['offset']

        self.mqtt_client = mqtt_client
        self.logger = logging.getLogger(__name__)

        self.first_read_after_startup = True

        self.value_day_d1 = ""
        self.day_d1 = datetime.today().day

    def convert_current_data_to_unit(self, data):
        """Convert data to unit"""
        val_mv = self.convert_data_to_mV(data)
        val_ma = self.convert_mV_to_mA(val_mv)
        cal_val_scaled = self.convert_mA_to_unit(val_ma)
        return cal_val_scaled

    @abstractmethod
    def convert_voltage_data_to_unit(self, data):
        """Convert Voltage to unit"""
        pass

    @abstractmethod
    def convert_data_to_mV(self, data):
        """Convert data to mV"""
        pass

    @abstractmethod
    def send_value_over_mqtt(self):
        """Send value over MQTT"""
        pass

    def read_i2c_value(self, register):
        """Read I2C Value"""
        write = i2c_msg.write(self.i2c_address, (f'{register}'))
        read = i2c_msg.read(self.i2c_address, 2)
        self.bus.i2c_rdwr(write, read)
        return read

    def convert_mV_to_mA(self, val_mv):
        """Convert mV to mA"""
        val_ma = val_mv / self.shunt    # +/- 10 ohm
        return val_ma

    def convert_mA_to_unit(self, val_ma):
        """Convert mA to Unit"""
        cal_val = val_ma - self.calibration_low_mA
        scale = self.full_range_value / \
            (self.calibration_high_mA - self.calibration_low_mA)
        #print (f"scale = {scale}   cal_valm = {cal_val}")
        cal_val_scaled = round(cal_val * scale, 1)
        return float(cal_val_scaled) + float(self.offset)

    def print_value(self, register, data):
        """Print Value"""
        print_data = f'REGISTER: ' + hex(register) + " : "
        for value in data:
            print_data = print_data + " " + hex(value) + "\t"
        val = int.from_bytes(data, byteorder='big')
        if (register == 1):
            val_mv = self.convert_data_to_mV(data)
            val_ma = self.convert_mV_to_mA(val_mv)
            cal_val_scaled = self.convert_mA_to_unit(val_ma)
            print_data = print_data + " " + str(val) + "\t" + str(val_mv) + "mV" + "\t" + str(
                val_ma) + "mA" + "\t" + str(cal_val_scaled) + self.unit
        if (register == 2):
            val_mv = self.convert_voltage_data_to_unit(data)
            # val_mv = val / 2000 # /8 * 4mV
            print_data = print_data + " " + str(val) + "\t" + str(val_mv) + "V"

        self.logger.info("%s   <--- use this info to calibrate", print_data)

    def read_i2c_all_registers(self):     # the bus must be OPEN!!
        """Read I2C All Registers"""
        for i in range(0, 6):
            read = self.read_i2c_value(i)
            self.print_value(i, read)

    def activate_100s_action(self):
        """Activate 100s action"""
      #  pass

    def on_exit(self):
        """ Do this on exit """
       # pass
