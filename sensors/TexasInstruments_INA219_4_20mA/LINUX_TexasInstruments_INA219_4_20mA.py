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


import logging
import time

from smbus2 import SMBus, i2c_msg  # https://pypi.org/project/smbus2/

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

REG_CONFIG = 0x00
REG_SHUNT_VOLTAGE = 0x01
REG_BUS_VOLTAGE = 0x02
REG_POWER = 0x03
REG_CURRENT = 0x04
REG_CALIBRATION = 0x05

REG_CONFIG_VALUE_RUN = [REG_CONFIG, 0x1F, 0xFF]
REG_CONFIG_VALUE_POWER_DOWN = [REG_CONFIG, 0x1F, 0xF8]


class LINUX_TexasInstruments_INA219_4_20mA(Sensor):
  

  def __init__(self, mqtt_client, aSensor,mqtt_top_dir_name):    
    super().__init__("LINUX","TexasInstruments", "INA219 4-20mA", "Current","I2C" ,mqtt_client, aSensor)

    self.mqtt_top_dir_name = mqtt_top_dir_name
    self.mqtt_sub_dir         = aSensor['mqtt_sub_dir']
    self.i2c_channel          = aSensor['channel']  # "/dev/i2c-1"  = 1
    self.i2c_address          = aSensor['address']      
    self.calibration_low_mA   = aSensor['calibration_low_mA']
    self.calibration_high_mA  = aSensor['calibration_high_mA']
    self.full_range_value     = aSensor['full_range_value']
    self.unit                 = aSensor['unit']
    self.mqtt_function_name   = aSensor['mqtt_function_name']
    self.shunt                = aSensor['shunt_resistor']

    self.mqtt_client = mqtt_client
    self.logger = logging.getLogger(__name__)


    self.bus = SMBus(self.i2c_channel)
    write = i2c_msg.write(self.i2c_address, REG_CONFIG_VALUE_POWER_DOWN)
    self.bus.i2c_rdwr(write)

    #self.read_i2c_all_registers()  # See all registers from the INA219 chipset

    self.bus.close()

  def convert_voltage_data_to_unit(self, data):
    val = int.from_bytes(data, byteorder='big')
    val_mV = val / 2000 # /8 * 4mV
    return val_mV


  def convert_current_data_to_unit(self, data):
    val_mV = self.convert_data_to_mV(data)
    val_mA = self.convert_mV_to_mA(val_mV)
    cal_val_scaled = self.convert_mA_to_unit(val_mA)
    return cal_val_scaled

  def convert_data_to_mV(self, data):
    val = int.from_bytes(data, byteorder='big')
    val_mV = val / 100
    return val_mV

  def convert_mV_to_mA(self, val_mV):
    val_mA = val_mV  / self.shunt    # +/- 10 ohm
    return val_mA

  def convert_mA_to_unit(self, val_mA):
    cal_val = val_mA - self.calibration_low_mA
    scale = self.full_range_value / (self.calibration_high_mA - self.calibration_low_mA)
    cal_val_scaled = round(cal_val * scale  ,1)
    return cal_val_scaled

  def read_i2c_value(self, register):
      write = i2c_msg.write(self.i2c_address, (f'{register}'))    
      read = i2c_msg.read(self.i2c_address, 2)
      self.bus.i2c_rdwr(write, read)
      return read
  def print_value(self, register, data):
      printData = f'REGISTER: ' + hex (register) + " : "   
      for value in data:
        printData = printData + " " + hex(value) + "\t"
      val = int.from_bytes(data, byteorder='big')
      if (register == 1) :         
        val_mV = self.convert_data_to_mV(data)
        val_mA = self.convert_mV_to_mA(val_mV)
        cal_val_scaled = self.convert_mA_to_unit(val_mA)
        printData = printData + " " + str(val) + "\t" + str(val_mV) + "mV" + "\t" + str(val_mA) + "mA" + "\t" + str(cal_val_scaled) + self.unit
      if (register == 2) : 
        val_mV = self.convert_voltage_data_to_unit(data)        
        #val_mV = val / 2000 # /8 * 4mV
        printData = printData + " " + str(val) + "\t" + str(val_mV) + "V" 
      self.logger.info(printData + "   <--- use this info to calibrate")

  def read_i2c_all_registers(self):     # the bus must be OPEN!!
    for i in range(0,6):      
      read = self.read_i2c_value(i)
      self.print_value(i,read)  


  def send_value_over_mqtt(self): 
    #print("Start convertion")

    self.bus = SMBus(self.i2c_channel)
    write = i2c_msg.write(self.i2c_address, REG_CONFIG_VALUE_RUN)
    self.bus.i2c_rdwr(write)
    time.sleep(0.3)    
    # ------------------------------------------------------------------------------
    register = REG_SHUNT_VOLTAGE
    read = self.read_i2c_value(register)
    self.print_value(register,read) 
    sensor_value = self.convert_current_data_to_unit(read)
    mqtt_dir = f"{self.mqtt_top_dir_name}/{self.mqtt_sub_dir}/{self.mqtt_function_name}" 
    self.mqtt_client.publish(mqtt_dir, sensor_value)
    self.logger.info(f"    MQTT: {mqtt_dir}  {sensor_value}") 
    # ------------------------------------------------------------------------------
    register = REG_BUS_VOLTAGE
    read = self.read_i2c_value(register)
    #self.print_value(register,read) 
    sensor_value = self.convert_voltage_data_to_unit(read)
    mqtt_dir = f"{self.mqtt_top_dir_name}/{self.mqtt_sub_dir}/bus-voltage" 
    self.mqtt_client.publish(mqtt_dir, sensor_value)
    self.logger.info(f"    MQTT: {mqtt_dir}  {sensor_value}") 
    # ------------------------------------------------------------------------------
    self.bus.close()


  def activate_100s_action(self):
    pass
  
  def on_exit(self):
    pass

#class LINUX_TexasInstruments_INA219_4_20mA(Sensor):
#  
#
#  def __init__(self, mqtt_client, config):    
#    super().__init__("LINUX","TexasInstruments", "INA219 4-20mA", "Current","I2C" ,mqtt_client, config)
#    
#    self.mySensorList = []
#    
#    #print(f'{self.parameters}')
#
#    for sensor in self.parameters: 
#      self.mySensorList.append(my_ti_ina219_sensor(mqtt_client,sensor) )
#
#      
#  def send_value_over_mqtt(self,mqtt_top_dir_name): 
#
#    #print("in INA TOP")
#    for x in self.mySensorList:
#      x.send_value_over_mqtt(mqtt_top_dir_name)
#
##  
#  def activate_100s_action(self):
#    pass
#  
#  def on_exit(self):
#    pass