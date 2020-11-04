Status: under development - Validating the counter to the official city gas counter

# Sensor Description
This sensor will send the host system information.
 - Platform information (static)
 - CPU usage (dynamic)
 - Memory usage (dynamic)
 - Disk usage (dynamic)

There are 2 different JSON messages:
 - Static: with all static data
 ![screenshot](static.png?raw=true)
 - Dynamic: with all changing info
 ![screenshot](dynamic.png?raw=true)
 

## Setup on Raspberry pi 
  see:[example_settings.yaml](example_settings.yaml)
  
## Use with home-assistant
Update your sensors section in configuration.yml with the new mqtt topics, for example:

# Example configuration.yaml entry
TODO


# Example ui-lovelace.yaml entry
TODO


# Hardware setup:
no additional hardware needed

# Used Applications
 - Application 01: Monitor the system
 - Application 02: Still alive? if not take some actions, like send a message in Home Assistant
