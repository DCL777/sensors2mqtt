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


import paho.mqtt.client as mqtt
import paho.mqtt.publish as publishpython
import yaml
import RPi.GPIO as GPIO

from time import sleep, time
from Sensor import Sensor

class RPI_Generic_Ultrasonic(Sensor):
  def __init__(self, mqtt_client, sensorParameters,mqtt_top_dir_name):
    super().__init__("RPI","Generic", "Ultrasonic", "Ultrasonic","PING Mode",mqtt_client, sensorParameters)

    self.mqtt_top_dir_name = mqtt_top_dir_name
    self.sensorParameters = sensorParameters
    self.mqtt_client = mqtt_client

    self.echo_pin = sensorParameters['echo_pin']
    self.trigger_pin = sensorParameters['trigger_pin']
    self.sample_size = sensorParameters['sample_size']
    self.scale_factor = sensorParameters['output_scale_factor']
    self.decimal_points = sensorParameters['output_round_decimal_point']
    self.output_value_min = sensorParameters['output_value_min']
    self.output_value_max = sensorParameters['output_value_max']    
    self.trigger_pulse_time = sensorParameters['trigger_pulse_time']
    self.delay_between_measurements = sensorParameters['delay_between_measurements']
    
    
    self.gpio_mode = GPIO.BCM
    #self.logger = logging.getLogger(__name__)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.trigger_pin, GPIO.OUT)      
    GPIO.setup(self.echo_pin, GPIO.IN)

  def ping(self):
    pulse_duration_total = 0
    
    for i in range(self.sample_size):
      # Get distance measurement
      GPIO.output(self.trigger_pin, GPIO.LOW)         	# Set TRIG LOW
      sleep(self.delay_between_measurements)                                       	# Min gap between measurements        

      # Create 10 us pulse on TRIG
      GPIO.output(self.trigger_pin, GPIO.HIGH)          # Set TRIG HIGH
      sleep(self.trigger_pulse_time)                                   	# Delay 10 us
      GPIO.output(self.trigger_pin, GPIO.LOW)           # Set TRIG LOW

      # Measure return echo pulse duration
      while GPIO.input(self.echo_pin) == GPIO.LOW:     # Wait until ECHO is LOW
          pulse_start = time()                         # Save pulse start time
      while GPIO.input(self.echo_pin) == GPIO.HIGH:    # Wait until ECHO is HIGH
          pulse_end = time()                           # Save pulse end time
      pulse_duration = pulse_end - pulse_start 
      
      pulse_duration_total = pulse_duration_total + pulse_duration
      
      
    
    pulse_duration_average = pulse_duration_total / self.sample_size
    # Distance = 34300/2 * Time (unit cm) at sea level and 20C
    distance = (ulse_duration_average * self.scale_factor)         # Calculate distance:  34300/2
    distance = round(distance, decimal_points)                    # Round to two decimal points

      if distance > self.output_value_min and distance < output_value_max:              # Check distance is in sensor range
          distance = distance
      else:
          distance = 0
      return distance


  def send_value_over_mqtt(self): 
    sensor_value = self.ping()
    mqtt_sub_dir = self.parameters['mqtt_sub_dir']
    friendly_name = f"{self.mqtt_top_dir_name}/{self.sensorParameters['mqtt_sub_dir']}/{self.sensorParameters['mqtt_function_name']}"
    self.mqtt_client.publish(friendly_name, sensor_value)
    self.logger.info(f"MQTT: {friendly_name}  {sensor_value}")

  def on_exit(self):
    GPIO.cleanup()
