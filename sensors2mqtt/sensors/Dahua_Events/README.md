Status: Under test: only tested with CrossLineDetection

# Sensor Description
This sensor will send the dahua nvr events to mqtt.
example mqtt event:
{"action": "Stop", "Direction": "RightToLeft", "UTC": 1654947226.0, "Name": "toegang", "ObjectType": "Human", "Area": 909.312}

The Area can be used to define the size of the object.  When it's to small, it is likly an animal.  

"""
Dahua IP Camera events to MQTT app. Implemented from: https://github.com/johnnyletrois/dahua-watch


According to the API docs, these events are available: (availability depends on your device and firmware)

 - VideoMotion: motion detection event
 - VideoLoss: video loss detection event
 - VideoBlind: video blind detection event.
 - AlarmLocal: alarm detection event.
 - CrossLineDetection: tripwire event
 - CrossRegionDetection: intrusion event
 - LeftDetection: abandoned object detection
 - TakenAwayDetection: missing object detection
 - VideoAbnormalDetection: scene change event
 - FaceDetection: face detect event
 - AudioMutation: intensity change
 - AudioAnomaly: input abnormal
 - VideoUnFocus: defocus detect event
 - WanderDetection: loitering detection event
 - RioterDetection: People Gathering event
 - ParkingDetection: parking detection event
 - MoveDetection: fast moving event
 - MDResult: motion detection data reporting event. The motion detect window contains 18 rows and 22 columns. The event info contains motion detect data with mask of every row.
 - HeatImagingTemper: temperature alarm event

And here are some events that might work:

 - TemperatureAlarm
 - BatteryLowPower
 - IPConflict
 - HotPlug
 - StorageLowSpace
 - StorageFormat
 - StorageNotExist
 - ChassisIntruded
"""


## Setup on Raspberry pi 
  see: [example_settings.yaml](example_settings.yaml)
  
## Use with home-assistant
Update your sensors section in configuration.yaml with the new mqtt topics, for example:
```
  - alias: "CrossLineDetection event example"
    mode: single
    trigger:
      - platform: mqtt
        topic: 'cameras/nvr/10/CrossLineDetection'    
    action:
```

# Example configuration.yaml entry

no update needed

# Example ui-lovelace.yaml entry

no update needed

# Hardware setup:
Dahua Camera or NVR

# Used Applications

use the Dahua Camera as alarm or bel
