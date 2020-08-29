# sensors2mqtt
Universal Sensor data transporter over MQTT.  Sensor like water flow sensor (=pulse-counter), DS18S20 , INA219,...  

Supported sensors at the moment:
- Maximintegrated_DS18S20
- Generic_PulseCounter

Under development:
- TexasInstruments_INA219 



# How to add more sensors? 
- copy and rename an existing sensor
- change the file name & the class name
    - [manufacturer]_[partnumber]
    - or Generic_[function]
- change the content for your function
- The filename & class name must be exact (case sensitive) equal
- use the class name in 'sensors_settings.yaml' to activate the new module (dynamic loaded)


## Config your sensors & MQTT broker info
Edit sensors.yml to add or remove sensors
Only sensors define here will be loaded at runtime

or start with argument: -c option:
./sensors2mqtt.py -c my_sensor_data.yaml



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

## Setup

Configure your rapsberry pi where the sensors are attachted:
- download the latest version of 'Raspberry Pi OS (32-bit) Lite' here: https://www.raspberrypi.org/downloads/raspberry-pi-os/
- enable SSH by adding a file named 'SSH' into the boot location
- if 1-wire is required (for DS18B20)
  - enable one-wire in config.txt (on your SD-Card) => with the correct pin number
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
=> ./sensors2mqtt.py
```

Hardware setup:
![screenshot](docs/images/hw.png?raw=true)

some hardware comments:
- DS18S20: needs a pull up resistor of 4k7
- my water flow puls counter works at 5VDC.  RPI needs 3V3 GPIO: so a resistor divider is used to lower the voltages
- INA219: change the shunt resistor to 10 ohm to have a good measurement
- Boost converter will convert the 5VDC to 12.5VDC needed for the 'Submersible Water Level Transducer Sensor'


Special thanks to https://github.com/engonzal/DS18B20-mqtt
