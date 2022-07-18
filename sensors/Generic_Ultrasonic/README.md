Status: Under development

# Sensor Description
This is generic PING-MODE ultrasonic sensor.  A pulse can defined at the trigger, and the response time is calculated. 

Examples: JSN-SR04T, JSN-SR04T-2.0, JSN-SR04T-3.0, HC-SR04, HY-SRF05, US-100 and other ultrasonic modules. 
datasheet: [JSN-SR04T-2.0.pdf](JSN-SR04T-2.0.pdf)
example hardware: https://aliexpress.com/item/1005003683104654.html
```
    trigger_pulse_time: 0.00001   # puls of 10 us needed for JSN-SR04T-2.0, see datasheet for your ultrasonic sensor
    delay_between_measurements: 0.1  # 100 ms
```



## Setup on Raspberry pi 
  - pip install RPi.GPIO


## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:

```
sensor:
  - platform: mqtt
    state_topic: "garage/ultrasonic/height"
    name: "Citern Water Height ultrasonic"
    icon: mdi:water-pump
    unit_of_measurement: "mm"
	
	
```


# Hardware setup:
Choose a trigger pin and an echo pin & configure in the settings 
```
    echo_pin: 21
    trigger_pin: 20
```