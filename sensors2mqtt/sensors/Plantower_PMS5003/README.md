Status: Under development

# Sensor Description
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

  Circuit Attentions  (copied for datasheet)
  1) DC 5V power supply is needed because the FAN should be driven by 5V.
     But the high level of data pin is 3.3V. Level conversion unit should be
     used if the power of host MCU is 5V.
  2) The SET and RESET pins are pulled up inside so they should not be
     connected if without usage.
  3) PIN7 and PIN8 should not be connected.
  4) Stable data should be got at least 30 seconds after the sensor wakeup
     from the sleep mode because of the fan’s performance

## Setup on Linux 
  see: [example_settings.yaml](example_settings.yaml)
  
## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:

# Example configuration.yaml entry
```
TODO
```

# Example ui-lovelace.yaml entry
```
TODO
```

# Hardware setup:
![screenshot](PMS5003_03.PNG?raw=true)



