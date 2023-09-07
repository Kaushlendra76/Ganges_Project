
import paho.mqtt.client as mqtt
from time import gmtime,strftime
from threading import Timer, Thread, Event
import time
import datetime
import json
import threading
from datetime import datetime
import logging
import queue
import Global
import XbeeDevice
import filelogger
import pickle
from collections import OrderedDict
import ssl
import dynamoDB
#import RPi.GPIO as GPIO




#private reference to the mqtt client object for which we reserve a mem loc from the start
_mqttClient = None

mqtt_message=[]
mqtt_topic=[]
index=0
livepackets_list=[]

#GANGES/0013A20041BFB524/COMMAND/GET

#log=filelogger.DataLogger()

#has to be provided by the module consumer:

on_message = None
'callback for receiving values from the IOT platform: expects 3 params: deviceId, assetId, payload'
GatewayId = None
'the id of the gateway that we are using.'


#optionally provided by the module consumer
on_connected = None
'callback that will be signalled once the broker is connected. This can be used to block' \
'the application untill a connection with the broker has been made, so that no data gets lost'



class MqttThreadedClient(threading.Thread):

    def __init__(self, mqttpackets,devicepackets,devicecommandid,MAC_DICT,**kwds):
        
        global myMAC
       
        
        #mqttServer = "m10.cloudmqtt.com"
        #port = 16674
        self.DB=dynamoDB.dynamoDB()
        self.GatewayId=  Global.myMAC
        self._mqttClient = mqtt.Client()
        #self._mqttClient.username_pw_set("qtyywdeu", "gieXmgeRD24Y");
        #self._mqttClient.connect(mqttServer, port, 60)
        
        self._mqttClient.tls_set(ca_certs="/home/pi/Ganges_working/cert/rootCA.pem", certfile="/home/pi/Ganges_working/cert/d4fff810a13848c9c3c2a47c67ce8ff2ecce3d541badadb6804a1168e7fe452b-certificate.pem.crt", keyfile="/home/pi/Ganges_working/cert/d4fff810a13848c9c3c2a47c67ce8ff2ecce3d541badadb6804a1168e7fe452b-private.pem.key", tls_version=ssl.PROTOCOL_SSLv23)
        self._mqttClient.tls_insecure_set(True)
        self._mqttClient.connect("a1j5yyujkq8kkx-ats.iot.ap-south-1.amazonaws.com", 8883, 60) 
        #self._mqttClient.subscribe("test/topic")
        self._mqttClient.on_connect = self._on_connect
        self._mqttClient.on_message = self._on_MQTTmessage
        
        self.mqtttopicpackets = queue.Queue() #mqtttopicpackets
        self.mqttpayloadpackets = queue.Queue() #mqttpayloadpackets
        
        self.mqttsendpackets = mqttpackets
        self.devicesendpackets = devicepackets
        self.devicecommandid = devicecommandid

        self._mqttClient.loop_start()
        self.mqttstopflag = 0
        self.gateway=self.GatewayId.decode('UTF-8')
        
        threading.Thread.__init__(self, **kwds)


    def _on_connect(self,client, userdata, rc,flag):
        
        #subscribe to the topics for the device
        print("mqtt _on_connect: Connected with result code "+str(rc))
        
        subtopic1= "GANGES/"+ self.gateway +"/COMMAND/GET"
        subtopic2= "GANGES/"+ self.gateway +"/COMMAND/SET"
        print(subtopic1)
        print(subtopic2)
        self._mqttClient.subscribe(subtopic1)
        self._mqttClient.subscribe(subtopic2)
    
    def _on_MQTTmessage(self,client, userdata, msg):
        'The callback for when a PUBLISH message is received from the server.'

        #print ("Incoming message ")
        payload = msg.payload.decode('utf-8')
        print ("Incoming message - topic: " + msg.topic + ", payload: " + payload)

        self.mqttpayloadpackets.put(payload)
        self.mqtttopicpackets.put(msg.topic)

    def sendLiveData(self,toSend):
        """send the data to the cloud. Data can be a single value or object
        """
        #topic = "EMS/EVOLUTE/" + self.GatewayId + "/Live"
        topic = "GANGES/"+ self.gateway +"/Data/Live"
        print("Publishing message - topic: " + topic + ", payload: " + toSend)
        self._mqttClient.publish(topic, toSend, 2, False)
        self.DB.updateDB()


    def sendResponse(self,toSend):
        print("Sending MQTT Data")
        topic = "GANGES/"+ self.gateway +"/COMMAND/RESPONSE"
        print("Publishing message - topic: " + topic + ", payload: " + toSend)
        self._mqttClient.publish(topic, toSend, 0, False)
        
    def myAtoi(self,string):
        
        res = 0

        for i in xrange(len(string)):

            res = res*10 + (ord(string[i]) - ord('0'))

        print ('result is ' ,res)
        return res
        

    def run(self):
        global newmac_Dict
        global commandtype
        global devicelistflag
        Global.newmac_Dict=OrderedDict()
        
        try:
            


        # Extract the first item from the command queue
            while not(self.mqttstopflag):
                #print(" MQTT Runing! ")
                if not self.devicesendpackets.empty():
                    try:
                        
                        if Global.DeviceReg == 1:
                        #device_data = self.devicesendpackets.get()
                        #self.sendResponse(device_data)
                            print("This is MQTT Data")
                            deviceid = self.devicecommandid.get()
                            if deviceid == "01":
                                device_data = self.devicesendpackets.get()
                                self.sendLiveData(device_data)
                            if deviceid == "02":
                                device_data = self.devicesendpackets.get()
                                self.sendLiveData(device_data)
                            if deviceid == "03":
                                device_data = self.devicesendpackets.get()
                                self.sendLiveData(device_data)
                            if deviceid == "06":
                                device_data = self.devicesendpackets.get()
                                self.sendResponse(device_data)
                            if deviceid == "07":
                                device_data = self.devicesendpackets.get()
                                self.sendResponse(device_data)
                            # print(commandtype)
                            # if commandtype == "GET" or commandtype == "SET":
                            #     device_data = self.devicesendpackets.get()
                            #     self.sendResponse(device_data)
                            # else:
                            #     self.sendLiveData(device_data)
                            

                              
                    except Exception as e:
                        print (e)
                    finally:
                        pass

                if not self.mqtttopicpackets.empty():
                    print ("new packet found")
                    topic_data = self.mqtttopicpackets.get()
                    mqttmessage = self.mqttpayloadpackets.get()
                    #mqttmessage = mqttmessage.decode(utf-8)
                    print (mqttmessage)
                    mqttmessage=json.loads(mqttmessage)
                    commandtype =  (topic_data.split('/'))[3]
                    print( commandtype,'\n' )
                
                    #log.message(mqttmessage)

                    if commandtype == 'SET':
                        try:
                            
                            print ("GET Command Processing\n")
                            #mqttmessage=json.loads(mqttmessage)
                            commandID=mqttmessage["CommandID"]
                            command=mqttmessage["Command"]
                            mqttcommandlist = []

                            if len(mqttmessage)<=2:
                        
                                print ("We Dont Got the Device list")
                                liststatus=0
                            else:
                                print ("We Got the Device List")
                                liststatus=1
        
                                devicelist_keys=[]

                                for keys in mqttmessage.keys():
                                    devicelist_keys.append(keys)
                                devicelist_keys.remove("Command")
                                devicelist_keys.remove("CommandID")

                                for keys in devicelist_keys:
                                    if mqttmessage.has_key(keys):
                                        Device_mac=mqttmessage[keys]['MacAddress']
                                        Device_no=mqttmessage[keys]["SN"]
                                        Global.newmac_Dict.update([(Device_mac,Device_no)])
                                        #Global.mac_Dict.update([(Device_mac,Device_no)])
                                print (Global.newmac_Dict)
                                #log.message(Global.newmac_Dict)
                                # open a file and update
                            
                            
                                mqttcommandlist.append(commandtype)
                                for Device_mac in Global.newmac_Dict.keys():
                                    #print Device_mac
                                    Device_mac=Device_mac.decode("hex")
                                    mqttcommandlist.append(Device_mac)
                            
                                self.mqttsendpackets.put(mqttcommandlist)
                            
                                devicelistflag = 1

                            DevicelistPacket={}
                            DevicelistPacket["CommandID"]=commandID
                            DevicelistPacket["DDT"]=command
                            DevicelistPacket["MacAddress"]=self.GatewayId
                            DevicelistPacket["Status"]=liststatus
            
                            print (DevicelistPacket)
                            DevicelistPacket=json.dumps(DevicelistPacket)
                            self.sendResponse(DevicelistPacket)
                            self.mqttsendpackets.task_done()
                            #log.message(DevicelistPacket)
                        except Exception as e:
                            print (e)
                        finally:
                            pass
                


                    if commandtype == 'GET':
                        try:
                            
                            print ("GET command processing")
                            #mqttmessage=json.loads(mqttmessage)
                            address=mqttmessage["DID"]
                            serialno=mqttmessage["CMD"]
                            #Global.RegcommandID=mqttmessage["CommandID"]
                            #Global.Regcommand=mqttmessage["Command"]
                
                            #Macaddress=address.decode("hex")
                            
                            #mqttcommandlist = []
                            #Global.registerdict=OrderedDict()
                            #Global.registerdict.update([(address,serialno)])
                            #print (Global.registerdict)
                            #mqttcommandlist.append(commandtype)
                            #mqttcommandlist.append(Macaddress)
                            mqttmessage = json.dumps(mqttmessage)
                            self.mqttsendpackets.put(mqttmessage)
                            #self.mqttcommandstring.put(commandtype)
                            self.mqttsendpackets.task_done()
                        except Exception as e:
                            print (e)
                        finally:
                            pass

        except Exception as e:
            print (e)
        finally:
            pass















