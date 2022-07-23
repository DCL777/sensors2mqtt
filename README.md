
[![GitHub issues](https://img.shields.io/github/issues/DCL777/sensors2mqtt)](https://github.com/DCL777/sensors2mqtt/issues)
[![GitHub stars](https://img.shields.io/github/stars/DCL777/sensors2mqtt)](https://github.com/DCL777/sensors2mqtt/stargazers)
[![GitHub license](https://img.shields.io/github/license/DCL777/sensors2mqtt)](https://github.com/DCL777/sensors2mqtt/blob/master/LICENSE)
![GitHub top language](https://img.shields.io/github/languages/top/DCL777/sensors2mqtt)

# sensors2mqtt
Universal Sensor data transporter over MQTT.  Sensor like water flow sensor (=pulse-counter), DS18B20 , INA219,...  

For each sensor, an update can be choosen between:  10 (sec.) ,30,60, 300 (5min) , 900 (15min), 3600 (1h) , 10800 (3h), 21600 (6h) , 43200 (12h)

Supported sensors at the moment:
- Maximintegrated_DS18B20 temperature sensor
- Generic_PulseCounter
  - as a water-flow sensor
  - as gas meter counter
  - fully configurable for your application / sensor
- TexasInstruments_INA219_4_20mA 
  - as citern water height sensor. With a 'Submersible Water Level Transducer Sensor' 0-5m H2O  
  - fully configurable for your application
  - full range = 320mV, any current can be measured when the shunt resistor changes (not limited to 4-20mA)
- TexasInstruments_INA226_4_20mA 
  - as citern water height sensor. With a 'Submersible Water Level Transducer Sensor' 0-5m H2O  
  - fully configurable for your application
  - full range = 80mV, any current can be measured when the shunt resistor changes (not limited to 4-20mA)
- Generic_SystemInfo
  This sensor will send the following host system information:
   - Platform information (static)
   - CPU usage (dynamic)
   - Memory usage (dynamic)
   - Disk usage (dynamic) 
- Plantower_PMS5003
  This is a Digital universal particle concentration sensor
  Measures: 
   - PM1.0, PM2.5 & PM10  value for CF=1，standard particle & under atmospheric environment
   - The number of particles with diameter 
      - beyond 0.3 um in 0.1 L of air.
      - beyond 0.5 um in 0.1 L of air.
      - beyond 1.0 um in 0.1 L of air.
      - beyond 2.5 um in 0.1 L of air.
      - beyond 5.0 um in 0.1 L of air.
      - beyond 10  um in 0.1 L of air.

## How to add more sensors? 
- copy and rename an existing sensor
- change the directory to ```[manufacturer]_[partnumber]```
- change the file name & the class name
    - ```[platform]_[manufacturer]_[partnumber]```   
    - or ```[platform]_Generic_[function]```
- change the content for your function
- The filename & class name must be exact (case sensitive) equal
- use the class name in 'sensors_settings.yaml' to activate the new module (dynamic loaded)
- [platform]
    - 'LINUX' - should work on all linux platforms
    - 'RPI'   - should work on all Raspberry PI platforms
    - 'ESP32' - should work on all ESP32 platforms
    - ...
- The 'platform' must be a YAML parameter for your sensor


# Config your sensors & MQTT broker info
- copy sensors_settings.yaml to the same directory with a differend name: example: ```settings.yaml```
- Add or remove sensors in the new file.  Only sensors define here will be loaded at runtime
- Start with argument: -c option: ```./sensors2mqtt.py -c settings.yaml```
- Start with argument: -l option: ```./sensors2mqtt.py -c settings.yaml -l debug``` to get debug loggings


# Setup
## on a Raspberry pi
Configure your rapsberry pi where the sensors are attachted:
- download the latest version of 'Raspberry Pi OS (32-bit) Lite' here: https://www.raspberrypi.org/downloads/raspberry-pi-os/
- enable SSH by adding a file named 'SSH' into the boot location
- if 1-wire is required (for DS18B20)
  - enable one-wire in config.txt (on your SD-Card) => with the correct pin number  (or in linux: ```sudo nano /boot/config.txt```)
  - ```dtoverlay=w1-gpio,gpiopin=22```
- If I2C is needed:
  - enable I2C in config.txt (on your SD-Card)
  - ```dtparam=i2c_arm=on```

   
- Start the Raspberry Pi with the prepared SD-Card
- connect over SSH | login
   - username: pi
   - password: raspberry
   - change your password with: 'passwd'

Download & Run: ```./single_file_setup```    
or execute the commands manually:

```bash
=> sudo apt update
=> sudo apt upgrade
=> sudo apt install git
=> sudo apt-get install i2c-tools    => for I2C only (like INA219)
=> sudo apt-get install python-smbus => for I2C only (like INA219)
=> sudo adduser pi i2c               => for I2C only (like INA219)
=> sudo reboot                       => for I2C only (like INA219)
=> sudo apt install python3-rpi.gpio
=> sudo apt-get install python3 
=> sudo apt-get install python3-pip
=> git clone https://github.com/DCL777/sensors2mqtt.git
=> cd sensors2mqtt
=> sudo pip3 install -r requirements.txt
=> chmod 777 ./sensors2mqtt.py
=> ./sensors2mqtt.py
```

## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:
```
- platform: mqtt
  state_topic: "Garage/Outside/Temperature"
  name: "Garage Temperature"
  unit_of_measurement: "°C"
- platform: mqtt
  state_topic: "Garage/Cistern/Temperature "
  name: "Cistern Temperature"
  unit_of_measurement: "°C"
```

# Hardware setup:
![screenshot](docs/images/hw.png?raw=true)

some hardware comments:
- DS18B20: needs a pull up resistor of 4k7
- my water flow puls counter works at 5VDC.  RPI needs 3V3 GPIO: so a resistor divider is used to lower the voltages
- INA219: change the shunt resistor to 10 ohm to have a good measurement
- Boost converter will convert the 5VDC to 12.5VDC needed for the 'Submersible Water Level Transducer Sensor'

# Example cli output: if level=logging.DEBUG
```
pi@regenputten:~/sensors2mqtt $ ./sensors2mqtt.py -c sensors_test.yaml
============================
Start Sensors to MQTT V0.0.1             2020-08-15 Dries Claerbout
============================
Start MQTT: Broker: 192.168.1.10 Username: ha

Sensors found
----------------------------------------------------------------------
 -> DS18B20      Maximintegrated         Temperature     1-Wire
    -> Sensor 1:
        -> path = /sys/bus/w1/devices/28-011939f0e24a/w1_slave
        -> mqtt_sub_dir = cistern
 -> PulseCounter         Generic         PulseCounter    GPIO
    -> Sensor 1:
        -> pin_number = 23
        -> mqtt_sub_dir = garden
        -> function = water-flow
    -> Sensor 2:
        -> pin_number = 24
        -> mqtt_sub_dir = home
        -> function = water-flow
 -> INA219 4-20mA        TexasInstruments        Current         I2C
    -> Sensor 1:
        -> address = 64
        -> mqtt_sub_dir = citern
        -> channel = 1
        -> calibration_low_mA = 3.96
        -> calibration_high_mA = 18.5
        -> full_range_value = 5000
        -> unit = mm
        -> mqtt_function_name = height
----------------------------------------------------------------------


2020-08-30 17:01:06,583 - DEBUG -
Starting main loop...
2020-08-30 17:01:06,585 - DEBUG - 10 seconds event 1598803266.5848727
2020-08-30 17:01:07,446 - INFO -     MQTT: garage/cistern/Temperature  20.937
2020-08-30 17:01:07,448 - INFO -     MQTT: garage/garden/water-flow/delta  0
2020-08-30 17:01:07,450 - INFO -     MQTT: garage/garden/water-flow/total  89
2020-08-30 17:01:07,453 - INFO -     MQTT: garage/home/water-flow/delta  0
2020-08-30 17:01:07,454 - INFO -     MQTT: garage/home/water-flow/total  15
2020-08-30 17:01:07,760 - INFO -     MQTT: garage/citern/height  19.567
2020-08-30 17:01:07,764 - INFO -     MQTT: garage/citern/bus-voltage  12.517
2020-08-30 17:01:10,002 - DEBUG - 10 seconds event 1598803270.0023887
2020-08-30 17:01:10,886 - INFO -     MQTT: garage/cistern/Temperature  21.0
2020-08-30 17:01:10,888 - INFO -     MQTT: garage/garden/water-flow/delta  0
2020-08-30 17:01:10,890 - INFO -     MQTT: garage/garden/water-flow/total  89
2020-08-30 17:01:10,891 - INFO -     MQTT: garage/home/water-flow/delta  0
2020-08-30 17:01:10,893 - INFO -     MQTT: garage/home/water-flow/total  15
2020-08-30 17:01:11,199 - INFO -     MQTT: garage/citern/height  19.567
2020-08-30 17:01:11,202 - INFO -     MQTT: garage/citern/bus-voltage  12.517
2020-08-30 17:01:20,009 - DEBUG - 10 seconds event 1598803280.0089643
2020-08-30 17:01:20,886 - INFO -     MQTT: garage/cistern/Temperature  20.937
2020-08-30 17:01:20,888 - INFO -     MQTT: garage/garden/water-flow/delta  0
2020-08-30 17:01:20,890 - INFO -     MQTT: garage/garden/water-flow/total  89
2020-08-30 17:01:20,892 - INFO -     MQTT: garage/home/water-flow/delta  0
2020-08-30 17:01:20,893 - INFO -     MQTT: garage/home/water-flow/total  15
2020-08-30 17:01:21,199 - INFO -     MQTT: garage/citern/height  19.567
2020-08-30 17:01:21,202 - INFO -     MQTT: garage/citern/bus-voltage  12.517
```
# Start at boot-time  (tested on raspberry-pi-os)

1. create a configuration file
```
sudo nano /lib/systemd/system/sensors2mqtt.service
```

2. set the content to: 
```
[Unit]
Description=Sensors to MQTT Service
After=multi-user.target


[Service]
Type=idle
WorkingDirectory=/home/pi/sensors2mqtt/sensors2mqtt
ExecStart=/usr/bin/python3 /home/pi/sensors2mqtt/sensors2mqtt/sensors2mqtt.py -c settings.yaml

[Install]
WantedBy=multi-user.target

```
3. set ter permission to 644:
```
sudo chmod 644 /lib/systemd/system/sensors2mqtt.service
```
4. enable the service
```
sudo systemctl daemon-reload
sudo systemctl enable sensors2mqtt.service
```
5. reboot
```
sudo reboot
```

6. check the status for the service
```
sudo systemctl status sensors2mqtt.service
```
or 
```
ps aux | grep sensor
```

# Change RPI fixed IP-address

```
sudo nano /etc/dhcpcd.conf
```

look for the following section and change it:
```
interface eth0
static ip_address=192.168.1.12/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

# Special thanks to 
- https://pypi.org/project/smbus2/
- https://github.com/engonzal/DS18B20-mqtt
