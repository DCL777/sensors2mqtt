# Sensor Description
TODO

interface: RPi.GPIO

## Setup on Raspberry pi 
  - Nothing special


## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:

# Example configuration.yaml entry
```
sensor:
  - platform: mqtt
    name: "Stadswater Total"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'l'
    value_template: "{{ value_json.total }}"
    icon: mdi:water
  - platform: mqtt
    name: "Stadswater Delta"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'l'
    value_template: "{{ value_json.delta }}"
    icon: mdi:water
  - platform: mqtt
    name: "Stadswater Day"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'l'
    value_template: "{{ value_json.day }}"
    icon: mdi:water
  - platform: mqtt
    name: "Stadswater Month"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'm³'
    value_template: "{{ (value_json.month | float / 1000) | round(2)}}"
    icon: mdi:water
  - platform: mqtt
    name: "Stadswater Year"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'm³'
    value_template: "{{ (value_json.year | float / 1000) | round(2)}}"
    icon: mdi:water
  - platform: mqtt
    name: "Stadswater All"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'm³'
    value_template: "{{ (value_json.all | float / 1000) | round(2)}}"
    icon: mdi:water
``` 
# Example ui-lovelace.yaml entry
``` 
  - icon: mdi:water
    title: Water
    id: water
    background: radial-gradient(crimson, yellow)
    theme: dark-mode
    cards:
      - type: history-graph
        title: 'Water Total'
        entities:
            - entity: sensor.stadswater_total
              name: Stadswater              
        hours_to_show: 24
      - type: history-graph
        title: 'Water Delta'
        entities:
            - entity: sensor.stadswater_delta
              name: Stadswater              
        hours_to_show: 24
      - type: history-graph
        title: 'Water Day'
        entities:
            - entity: sensor.stadswater_day
              name: Stadswater              
        hours_to_show: 200
      - type: history-graph
        title: 'Water Month'
        entities:
            - entity: sensor.stadswater_month
              name: Stadswater              
        hours_to_show: 8000
      - type: history-graph
        title: 'Water Year'
        entities:
            - entity: sensor.stadswater_year
              name: Stadswater              
        hours_to_show: 200000
      - type: history-graph
        title: 'Water All'
        entities:
            - entity: sensor.stadswater_all
              name: Stadswater              
        hours_to_show: 200000

``` 

# Hardware setup:
![screenshot](../../docs/images/hw.png?raw=true)


