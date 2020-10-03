Status: finalized - working as expected - INA226 is a little bit more stable due to a longer sampling time and a higher oversampling.  But INA219 will do the job very fine.

# Sensor Description

INA219 Zerø-Drift, Bidirectional Current/Power Monitor With I2C Interface

datasheet: https://www.ti.com/lit/ds/symlink/ina219.pdf

interface: I2C

## Setup on Raspberry pi 
  - detect your I2C devices: 
  ```
  sudo i2cdetect -y 1
  ```

# Application 1: Measure Citern water height with: Submersible Water Level Transducer Sensor 0-5m H2O

## Hardware setup:
![screenshot](../../docs/images/hw.png?raw=true)

some hardware comments:
- The I2C-bus needs a pull up resistor of 2k2 (10k in some cases). Check your boards if it's installed.

# Calibration:

Calibration Settings:
  ```
    calibration_low_mA:  3.97679    #  4mA
    calibration_high_mA: 4.548219    # 20mA
    full_range_value:  192      # 5 mm = 20mA         0m = 4mA
  ```
console:
  ```
2020-09-16 08:07:06,243 - INFO - EVENT = 43200
2020-09-16 08:07:06,547 - INFO - REGISTER: 0x1 :  0x2c   0x66    11366  113.66mV        4.548219287715086mA     192.0mm   <--- use this info to calibrate
2020-09-16 08:07:06,548 - INFO -     MQTT: garage/citern1/height  192.0
2020-09-16 08:07:06,551 - INFO -     MQTT: garage/citern1/bus-voltage  12.421
2020-09-16 08:07:10,003 - INFO - EVENT = 10
2020-09-16 08:07:10,307 - INFO - REGISTER: 0x1 :  0x2b   0xfb    11259  112.59mV        4.505402160864346mA     177.6mm   <--- use this info to calibrate
2020-09-16 08:07:10,309 - INFO -     MQTT: garage/citern1/height  177.6
2020-09-16 08:07:10,312 - INFO -     MQTT: garage/citern1/bus-voltage  12.421
2020-09-16 08:07:20,010 - INFO - EVENT = 10
2020-09-16 08:07:20,313 - INFO - REGISTER: 0x1 :  0x26   0x98    9880   98.8mV  3.953581432573029mA     -7.8mm   <--- use this info to calibrate
2020-09-16 08:07:20,315 - INFO -     MQTT: garage/citern1/height  -7.8
2020-09-16 08:07:20,318 - INFO -     MQTT: garage/citern1/bus-voltage  12.441
2020-09-16 08:07:30,010 - INFO - EVENT = 30
2020-09-16 08:07:30,313 - INFO - REGISTER: 0x1 :  0x26   0xcd    9933   99.33mV 3.9747899159663866mA    -0.7mm   <--- use this info to calibrate
2020-09-16 08:07:30,315 - INFO -     MQTT: garage/citern1/height  -0.7
2020-09-16 08:07:30,318 - INFO -     MQTT: garage/citern1/bus-voltage  12.437
2020-09-16 08:07:40,010 - INFO - EVENT = 10
2020-09-16 08:07:40,313 - INFO - REGISTER: 0x1 :  0x26   0xd3    9939   99.39mV 3.9771908763505404mA    0.1mm   <--- use this info to calibrate
2020-09-16 08:07:40,315 - INFO -     MQTT: garage/citern1/height  0.1
2020-09-16 08:07:40,319 - INFO -     MQTT: garage/citern1/bus-voltage  12.437
  ```

Steps:
0. Make sure that the shunt resistor give you the desired range.  The INA-219 is set to full range = 320mV
1. place the sensor out of the water: write the current into the settings
  ```
    calibration_low_mA:  3.97679    #  4mA
  ```
2. place the sensor into the water: write the current into the settings and measure the heigth.
  ```
    calibration_high_mA:  3.97679    #  4mA
    full_range_value:  192      # 5 mm = 20mA         0m = 4mA
  ```  
  remark: the bigger the height the more accurate it will be
3. restart the software

## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:
```
sensor:
  - platform: mqtt
    state_topic: "garage/citern1/height"
    name: "Citern Water Height"
    value_template: "{{ (((value_json.value  | float)-260) * 0.016537988) | round(3) }}"
    icon: mdi:water-pump
    unit_of_measurement: "mm"
  - platform: mqtt
    name: citern_available_water
    state_topic: "garage/citern1/height"
    unit_of_measurement: 'm³'
    value_template: "{{ (((value_json.value  | float)-260) * 0.016537988) | round(3) }}"
    icon: mdi:water-pump
  - platform: mqtt
    name: citern_buffer
    state_topic: "garage/citern1/height"
    unit_of_measurement: 'Days'
    value_template: "{{ ((((value_json.value  | float)-260) * 16.537988) | round(3) / 137)| round(1)}}"
    icon: mdi:water-pump
  ```
    example GUI: ui-lovelace.yaml
  ```
        - type: entities
        show_header_toggle: false
        title: Citern water INA219
        entities:
          - entity: sensor.citern_available_water
            name: Available
          - entity: sensor.citern_water_height
            name: Water height
          - entity: sensor.citern_buffer
            name: Buffer 1                                        
      - type: history-graph
        title: 'Water height'
        entities:
            - entity: sensor.citern_water_height
              name: Height 1              
            - entity: sensor.citern_water_height_2
              name: Height 2              
        hours_to_show: 24
      - type: history-graph
        title: 'Water Buffer'
        entities:
            - entity: sensor.citern_buffer
              name: Buffer 1              
            - entity: sensor.citern_buffer_2
              name: Buffer 2              
        hours_to_show: 24
  ```
![screenshot](HA_INA219_01.PNG?raw=true)
![screenshot](HA_INA219_02.PNG?raw=true)


# Using InfluxDB & Grafana within Home Assistant 

![screenshot](grafana.png?raw=true)

