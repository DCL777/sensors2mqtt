Status: finalized - working as expected

# Sensor Description
This sensor will send the host system information.
 - Platform information (static)
 - CPU usage (dynamic)
 - Memory usage (dynamic)
 - Disk usage (dynamic)

There are 2 different JSON messages:
 - Static: with all static data
![screenshot](static.PNG?raw=true)
 - Dynamic: with all changing info
![screenshot](dynamic.PNG?raw=true)
 

## Setup on Raspberry pi 
  see: [example_settings.yaml](example_settings.yaml)
  
## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:

# Example configuration.yaml entry
```
sensor:
  - platform: mqtt
    state_topic: "TestPi/system_info/static"
    name: test_sysinfo_os
    value_template: "{{ value_json.System  }}  -  {{ value_json.Release  }}  on {{ value_json.Distribution  }}"
    icon: mdi:ip-network-outline
  - platform: mqtt
    state_topic: "TestPi/system_info/static"
    name: test_sysinfo_hw
    value_template: "{{ value_json.Machine  }}  -  {{ value_json.Architecture  }}  -  {{ value_json.CPU_Cores  }}-cores "
    icon: mdi:console-line
  - platform: mqtt
    state_topic: "TestPi/system_info/static"
    name: test_sysinfo_python
    value_template: "{{ value_json.Python_Version  }}"
    icon: mdi:language-python
  - platform: mqtt
    state_topic: "TestPi/system_info/static"
    name: test_sysinfo_nodename
    value_template: "{{ value_json.Node_Name  }}"
    icon: mdi:help-network
# ----------------------------------------------------------------    
  - platform: mqtt
    state_topic: "TestPi/system_info/dynamic"
    name: test_sysinfo_idle
    value_template: "{{ value_json.Idle_Percent  }}"
    icon: mdi:percent
    unit_of_measurement: '%'
  - platform: mqtt
    state_topic: "TestPi/system_info/dynamic"
    name: test_sysinfo_cpu
    value_template: "{{ value_json.CPU_Percent  }}"
    icon: mdi:percent
    unit_of_measurement: '%'
  - platform: mqtt
    state_topic: "TestPi/system_info/dynamic"
    name: test_sysinfo_mem
    value_template: "{{ value_json.MEM_Percent  }}"
    icon: mdi:memory
    unit_of_measurement: '%'
  - platform: mqtt
    state_topic: "TestPi/system_info/dynamic"
    name: test_sysinfo_disk
    value_template: "{{ value_json.DISK_Percent  }}"
    icon: mdi:harddisk
    unit_of_measurement: '%'
```

# Example ui-lovelace.yaml entry
```
  - icon: mdi:leaf
    title: Sensors
    id: rpi-sensors
    background: radial-gradient(crimson, yellow)
    theme: dark-mode
    cards:
      - type: entities
        title: 'System'
        entities:
          - entity: sensor.test_sysinfo_os
            name: OS
          - entity: sensor.test_sysinfo_hw
            name: Hardware
          - entity: sensor.test_sysinfo_python
            name: Python
          - entity: sensor.test_sysinfo_nodename
            name: 'Node Name'
      - type: history-graph
        title: 'System Stats'
        entities:
          - entity: sensor.test_sysinfo_idle
            name: Idle
          - entity: sensor.test_sysinfo_cpu
            name: CPU
          - entity: sensor.test_sysinfo_mem
            name: Memory
          - entity: sensor.test_sysinfo_disk
            name: Disk
        hours_to_show: 196
```

# Hardware setup:
no additional hardware needed

# Used Applications
 - Application 01: Monitor the system
 - Application 02: Still alive? if not take some actions, like send a message in Home Assistant
