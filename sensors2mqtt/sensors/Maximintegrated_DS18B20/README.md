Status: finalized - working as expected

# Sensor Description
The DS18B20 digital thermometer provides 9-bit to 12-bit Celsius temperature measurements and has an alarm function with nonvolatile user-programmable upper and lower trigger points. The DS18B20 communicates over a 1-Wire bus that by definition requires only one data line (and ground) for communication with a central microprocessor. In addition, the DS18B20 can derive power directly from the data line ("parasite power"), eliminating the need for an external power supply.

Each DS18B20 has a unique 64-bit serial code, which allows multiple DS18B20s to function on the same 1-Wire bus. Thus, it is simple to use one microprocessor to control many DS18B20s distributed over a large area. Applications that can benefit from this feature include HVAC environmental controls, temperature monitoring systems inside buildings, equipment, or machinery, and process monitoring and control systems.

datasheet: https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf 

interface: 1-wire

## Setup on Raspberry pi 
  - enable one-wire in config.txt (on your SD-Card) => with the correct pin number
  - ```dtoverlay=w1-gpio,gpiopin=22```


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
![screenshot](../../../docs/images/hw.png?raw=true)

some hardware comments:
- The 1-wire bus needs a pull up resistor of 4k7

