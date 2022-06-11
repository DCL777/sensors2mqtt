#!/usr/bin/python3
 
#  This file is part of the sensors2mqtt distribution (https://github.com/DCL777/sensors2mqtt.git).
#  Copyright (c) 2020 Dries Claerbout 
#  
#  This program is free software: you can redistribute it and/or modify  
#  it under the terms of the GNU General Public License as published by  
#  the Free Software Foundation, version 3.
#  
#  This program is distributed in the hope that it will be useful, but 
#  WITHOUT ANY WARRANTY; without even the implied warranty of 
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
#  General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License 
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


from cgi import print_form
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publishpython
import yaml
import logging
import json
import platform
import psutil
import time
import threading
import pycurl
from threading import Thread

import os.path
from os import path

from Sensor import Sensor
from datetime import datetime

URL_TEMPLATE = "http://{host}:{port}/cgi-bin/eventManager.cgi?action=attach&codes=%5B{events}%5D"

class LINUX_Generic_DahuaEvents(Sensor):

  proc = None
  cameras = []
  curl_multiobj = pycurl.CurlMulti()
  num_curlobj = 0
  kill_thread = False

  def __init__(self, mqtt_client, sensorParameters,mqtt_top_dir_name):    
    super().__init__("LINUX","Generic", "DahuaEvents", "DahuaEvents","Dahua Events" ,mqtt_client, sensorParameters)

    self.mqtt_top_dir_name =mqtt_top_dir_name


    self.sensorParameters = sensorParameters
    self.mqtt_client = mqtt_client

    self.mqtt_sub_dir   = sensorParameters['mqtt_sub_dir']

    #self.port = (sensorParameters['dahua_port'])
    #self.user = (sensorParameters['dahua_user'])
    #self.passw = (sensorParameters['dahua_pass'])
    #self.events = (sensorParameters['dahua_events'])
    self.logger = logging.getLogger(__name__)
   
    #self.myCameras = sensorParameters('cameras')
    

    #url = URL_TEMPLATE.format(**sensorParameters('cameras'))
    self.logger.info(f"LINUX_Generic_DahuaEvents")
    self.logger.info(f"-------------------------")



    for camera in self.sensorParameters["cameras"]:

          self.logger.info(f"camera: {camera} \n")
          mqtt_topic   = camera['mptt_topic']
          mqtt_dir = f"{self.mqtt_top_dir_name}/{self.mqtt_sub_dir}/{mqtt_topic}"

          dahuacam = DahuaCamera(camera, mqtt_client,mqtt_dir)
          self.cameras.append(dahuacam)
          url = URL_TEMPLATE.format(**camera)
          self.logger.info(f"Added Dahua device at: {url} \n") #Password: {config_mqtt['password']}")
#        # url = URL_TEMPLATE.format(**self.myCameras)
		  
          curlobj = pycurl.Curl()
          dahuacam.curlobj = curlobj
		  
          
          curlobj.setopt(pycurl.URL, url)
          curlobj.setopt(pycurl.CONNECTTIMEOUT, 30)
          curlobj.setopt(pycurl.TCP_KEEPALIVE, 1)
          curlobj.setopt(pycurl.TCP_KEEPIDLE, 30)
          curlobj.setopt(pycurl.TCP_KEEPINTVL, 15)
          curlobj.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_DIGEST)
          curlobj.setopt(pycurl.USERPWD, "{0}:{1}".format(camera["user"], camera["pass"]))
          curlobj.setopt(pycurl.WRITEFUNCTION, dahuacam.on_receive)
		  
          if "ignore_ssl" in camera and camera["ignore_ssl"] is True:
              curlobj.setopt(pycurl.SSL_VERIFYPEER, 0)   
              curlobj.setopt(pycurl.SSL_VERIFYHOST, 0)
          
          self.curl_multiobj.add_handle(curlobj)
          self.num_curlobj += 1
    
          self.logger.info(f"Starting thread")
          self.proc = Thread(target=self.thread_process)
          self.proc.daemon = False
          self.proc.start()

  def terminate(self):
      if self.proc and self.proc.is_alive():
          self.logger.info(f"Killing thread")
          self.kill_thread = True
          self.proc.join()
  def thread_process(self):
    while not self.kill_thread:
          ret, num_handles = self.curl_multiobj.perform()
          if ret != pycurl.E_CALL_MULTI_PERFORM:
              break
    while not self.kill_thread:
          ret = self.curl_multiobj.select(0.1)
          if ret == -1:
              self.on_timer()
              continue
          while not self.kill_thread:
             ret, num_handles = self.curl_multiobj.perform()
             if num_handles != self.num_curlobj:
                 _, success, error = self.curl_multiobj.info_read()
                 for curlobj in success:
                      camera = next(filter(lambda x: x.curlobj == curlobj, self.cameras))
                      if camera.reconnect:
                          continue
                      camera.on_disconnect("Success {0}".format(error))
                      camera.reconnect = time.time() + 5
                 for curlobj, errorno, errorstr in error:
                      camera = next(filter(lambda x: x.curlobj == curlobj, self.cameras))
                      if camera.reconnect:
                          continue
                      camera.on_disconnect("{0} ({1})".format(errorstr, errorno))
                      camera.reconnect = time.time() + 5
                 for camera in self.cameras:
                      if camera.reconnect and camera.reconnect < time.time():
                          self.curl_multiobj.remove_handle(camera.curlobj)
                          self.curl_multiobj.add_handle(camera.curlobj)
                          camera.reconnect = None
             if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
    self.logger.info(f"Thread exited")
  
  def send_value_over_mqtt(self): 
    None

  def on_exit(self):
    self.terminate()


class DahuaCamera:

    def __init__(self, camera, mqtt_client, mqtt_dir ):
#       self.hass = hass
        self.camera = camera
        self.curlobj = None
        self.connected = None
        self.reconnect = None
        self.mqtt_client = mqtt_client
        self.alarm = None
        self.logger = logging.getLogger(__name__)
        self.mqtt_dir = mqtt_dir

    def on_alarm(self, state):

        # Convert data from JSON string to JSON object
        if "data" in state:
            state["data"] = json.loads(state["data"])
        
        data = {}
        data["action"] = state["action"]
        data["Direction"] = state["data"]["Direction"]
        data["UTC"] = state["data"]["UTC"]
        data["Name"] = state["data"]["Name"]
        data["ObjectType"] = state["data"]["Object"]["ObjectType"]        
        xValue = state["data"]["Object"]["BoundingBox"][2] - state["data"]["Object"]["BoundingBox"][0]
        yValue = state["data"]["Object"]["BoundingBox"][3] - state["data"]["Object"]["BoundingBox"][1]
        xyValue = xValue * yValue
        data["Area"] = xyValue / 1000
        
        # NOT WORKING if state["index"] in self.camera["channels"]:
        # NOT WORKING   data["Location"] = self.camera["channels"][state["index"]]
        # NOT WORKING 

        json_data = json.dumps(data)
# EXAMPLE: JSON RAW DATA {"code": "CrossLineDetection", "action": "Start", "index": "15", 
# EXAMPLE: JSON RAW DATA "data": 
# EXAMPLE: JSON RAW DATA {
# EXAMPLE: JSON RAW DATA     "Class": "Normal", "CountInGroup": 1, "DetectLine": [[5529, 4888], [2560, 4256]], "Direction": "LeftToRight", "EventSeq": 21, "FrameSequence": 137528, "GroupID": 21, "IndexInGroup": 0, "LocaleTime": "2019-07-30 15:43:21", "Mark": 0, "Name": "Rule1", 
# EXAMPLE: JSON RAW DATA     "Object": 
# EXAMPLE: JSON RAW DATA     {
# EXAMPLE: JSON RAW DATA         "Action": "Appear", "BoundingBox": [4136, 1664, 5496, 7424], "Center": [4816, 4544], "Confidence": 0, "FrameSequence": 0, "LowerBodyColor": [0, 0, 0, 0], "MainColor": [0, 0, 0, 0], "ObjectID": 2627, "ObjectType": "Human", "RelativeID": 0, "Source": 0.0, "Speed": 0, "SpeedTypeInternal": 0
# EXAMPLE: JSON RAW DATA     }
# EXAMPLE: JSON RAW DATA     , "PTS": 42998760000.0, "RuleId": 1, "Sequence": 0, "Source": 36772624.0, "Track": null, "UTC": 1564472601.0, "UTCMS": 172
# EXAMPLE: JSON RAW DATA }
# EXAMPLE: JSON RAW DATA }

# EXAMPLE: code=CrossLineDetection;action=Start;index=15;data={
# EXAMPLE:    "Class" : "Normal",
# EXAMPLE:    "CountInGroup" : 1,
# EXAMPLE:    "DetectLine" : [
# EXAMPLE:       [ 5529, 4888 ],
# EXAMPLE:       [ 2560, 4256 ]
# EXAMPLE:    ],
# EXAMPLE:    "Direction" : "LeftToRight",
# EXAMPLE:    "EventSeq" : 21,
# EXAMPLE:    "FrameSequence" : 137528,
# EXAMPLE:    "GroupID" : 21,
# EXAMPLE:    "IndexInGroup" : 0,
# EXAMPLE:    "LocaleTime" : "2019-07-30 15:43:21",
# EXAMPLE:    "Mark" : 0,
# EXAMPLE:    "Name" : "Rule1",
# EXAMPLE:    "Object" : {
# EXAMPLE:       "Action" : "Appear",
# EXAMPLE:       "BoundingBox" : [ 4136, 1664, 5496, 7424 ],
# EXAMPLE:       "Center" : [ 4816, 4544 ],
# EXAMPLE:       "Confidence" : 0,
# EXAMPLE:       "FrameSequence" : 0,
# EXAMPLE:       "LowerBodyColor" : [ 0, 0, 0, 0 ],
# EXAMPLE:       "MainColor" : [ 0, 0, 0, 0 ],
# EXAMPLE:       "ObjectID" : 2627,
# EXAMPLE:       "ObjectType" : "Human",
# EXAMPLE:       "RelativeID" : 0,
# EXAMPLE:       "Source" : 0.0,
# EXAMPLE:       "Speed" : 0,
# EXAMPLE:       "SpeedTypeInternal" : 0
# EXAMPLE:    },
# EXAMPLE:    "PTS" : 42998760000.0,
# EXAMPLE:    "RuleId" : 1,
# EXAMPLE:    "Sequence" : 0,
# EXAMPLE:    "Source" : 36772624.0,
# EXAMPLE:    "Track" : null,
# EXAMPLE:    "UTC" : 1564472601.0,
# EXAMPLE:    "UTCMS" : 172

        # Publish two topics
 #       mqtt_data = {
        #   self.camera["topic"]: json.dumps(state),
        #   self.camera["topic"] + state["code"]: state["action"],
 #           self.camera["mptt_topic"] + state["index"] + "/" + state["code"]: json_data
 #       }

 #       for mptt_topic, payload in mqtt_data.items():
 #           mptt_topic = mptt_topic.strip("/")
 #       mqtt_dir = f"{self.mqtt_top_dir_name}/{self.mqtt_sub_dir}/{mqtt_topic}"
        index = state["index"]
        code = state["code"]
        
        mqtt_full_dir =  f"{self.mqtt_dir}/{index}/{code}"

        self.logger.info(f"    MQTT: {mqtt_full_dir}  {json_data}")
 #       self.logger.info(f"    MQTT: {self.mqtt_dir}  {json_data}")

        self.mqtt_client.publish(mqtt_full_dir, json_data)


       # self.hass.log("[{0}] Publishing MQTT. topic={1}, payload={2}".format(self.camera["host"], topic, payload))
       # self.hass.call_service("mqtt/publish", topic=topic, payload=payload)

    def on_connect(self):
#       self.hass.log("[{0}] OnConnect()".format(self.camera["host"]))
        self.connected = True

    def on_disconnect(self, reason):
#       self.hass.log("[{0}] OnDisconnect({1})".format(self.camera["host"], reason))
        self.connected = False

    def on_receive(self, data):
        decoded_data = data.decode("utf-8", errors="ignore")
        # self.hass.log("[{0}]: {1}".format(self.camera["host"], decoded_data))

        for line in decoded_data.split("\r\n"):
            if line == "HTTP/1.1 200 OK":
                self.on_connect()

            if not line.startswith("Code="):
                continue

            try:
                alarm = dict()
                for keyval in line.split(';'):
                    key, val = keyval.split('=')
                    alarm[key.lower()] = val

                self.parse_event(alarm)
            except Exception as ex:
                self.logger.info(f"Failed to parse: {ex}")

    def parse_event(self, alarm):
        # self.hass.log("[{0}] Parse Event ({1})".format(self.camera["host"], alarm))

        if alarm["code"] not in self.camera["events"].split(','):
            return

        self.on_alarm(alarm)