# Application Description

Reading the official city water meter by counting the pulses with a reed sensor

## Hardware setup 

Used platform: Raspberry PI 2B

![screenshot](Circuit.png?raw=true)

Practial:
![screenshot](water_meter.jpg?raw=true)

Used settings:
```
Sensors:
  Generic_PulseCounter:
  - pin_number: 17
    platform: RPI
    update_interval: 60 # seconds  10,30,60, 300 (5min) , 900 (15min), 3600 (1h) , 10800 (3h), 21600 (6h) , 43200 (12h)
    mqtt_sub_dir: stadswater
    function: water-flow  
    counter_scale: 0.1   
    pulse_scale: 2.5   
```

## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:

# Example configuration.yaml entry
```
sensor:
  - platform: mqtt
    state_topic: "zolder/stadswater/water-flow"
    name: city_water_meter_c
    value_template: "{{ (value_json.total | int) }}"
    icon: mdi:gas-station
    unit_of_measurement: "l"
``` 
# Example ui-lovelace.yaml entry
``` 
  - icon: mdi:water
    title: Tap Water
    id: water
    background: radial-gradient(crimson, yellow)
    theme: dark-mode
    cards:
      - type: entities
        show_header_toggle: false
        title: Tap water
        entities:
          - entity: sensor.city_water_meter_c
            name: Drinking Water Total
        
      - type: history-graph
        title: 'Water'
        entities:
            - entity: sensor.city_water_meter_c
              name: Drinking Water              
        hours_to_show: 24
``` 
![screenshot](HA.png?raw=true)

# Grafana:
![screenshot](grafana.png?raw=true)


