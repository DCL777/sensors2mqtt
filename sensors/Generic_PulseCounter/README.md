Status: under development - Validating the counter to the official city gas counter

# Sensor Description
Event counter counts every rising and falling edge.  Debounced at 10ms.  If linux is fast enough to process the pulses, 50Hz pulses can be captured.
 
This is a pulse counter for slow pulses (< 10Hz) only. Since the OS is linux, fast transition will not be captured.  When there is a lot of CPU load by other processes, pulses can be missed.

If higher frequency is required, there are some sollutions
  - using a microcontroller (MCU) (like PIC12F-series from microchip, atMega from Atmell, ...). Disadvantage is that it needs to be programmed.
  - using a I²C RTC with an event counter option like 
    - https://www.nxp.com/docs/en/data-sheet/PCF8583.pdf
    - https://datasheets.maximintegrated.com/en/ds/DS1678.pdf 
    - https://datasheets.maximintegrated.com/en/ds/DS1682.pdf 


interface: RPi.GPIO

## Setup on Raspberry pi 
  - after the first start, a file will be generated: pin_['pin number'].json
  ```
  \sensors2mqtt\sensors\Generic_PulseCounter\pin_17.json
  ```
  Edit this file to set the iniatial value of the counter.
  To start, the value's 'total', 'day', 'week', 'year' must be set to the same value.  The value of your official gas/water meter for example.

## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:

# Example configuration.yaml entry
```
sensor:
  - platform: mqtt
    name: "Drinking Water Total"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'm³'
    value_template: "{{ (value_json.total  | float / 1000) | round(4) }}"
    icon: mdi:water
  - platform: mqtt
    name: "Drinking Water Delta"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'l'
    value_template: "{{ value_json.delta }}"
    icon: mdi:water
  - platform: mqtt
    name: "Drinking Water Day"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'l'
    value_template: "{{ value_json.day }}"
    icon: mdi:water
  - platform: mqtt
    name: "Drinking Water Month"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'm³'
    value_template: "{{ (value_json.month | float / 1000) | round(2)}}"
    icon: mdi:water
  - platform: mqtt
    name: "Drinking Water Year"
    state_topic: "zolder/stadswater/water-flow"
    unit_of_measurement: 'm³'
    value_template: "{{ (value_json.year | float / 1000) | round(2)}}"
    icon: mdi:water
  - platform: mqtt
    name: "Drinking Water All"
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


