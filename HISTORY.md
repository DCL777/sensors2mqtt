# History

- LINUX_Generic_DahuaEvents changed to LINUX_Dahua_Events
## V0.0.1  2022-07-20
- Breaking Change: Changed Python source directory from ./Sensors2mqtt to ./Sensors2mqtt/Sensors2mqtt
  Action required: update the paths in:  /lib/systemd/system/sensors2mqtt.service see readme for the updated data
- Breaking Change: Additional package required.  run the command below again
  sudo pip3 install -r requirements.txt  
- Generic_SystemInfo: Fixed issue with python 3.8 and higher   (distro.like() deprecated)
- Generic_Ultrasonic: 
    - Fixed some running issues
	- Added Timeout, so it's not crashing when not connected
 