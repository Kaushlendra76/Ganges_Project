#   Copyright 2018-2019 AyKa Technologies
#


from xbee import ZigBee
import queue
import time
import serial
import pprint
import logging
import threading
import mqttcloud as IOT
import json
import XbeeDevice
import Livetimer
import pickle
import Global
import filelogger
import binascii
import paho.mqtt.client as mqtt
import ssl

import sys
import time
import datetime
import boto3
import time

import SDL_PCF8563

from uuid import getnode as get_mac
from collections import OrderedDict


#import RPi.GPIO as GPIO
#1.0013A20041BFB524
#2.0013A20041B4FF39
myMAC = ''
devices = []

# The XBee addresses I'm dealing with

# b'\x01FF\x02101C\x030.0,0.0,0.0,-8.1,-263.3,42.99,0,1,0,0,255,100,0\x04'
#b'\x01FF\x021111\x033\x04'


UNKNOWN = b'\xff\xfe'
xbeeindex=0
devicedata=[]
devicemac=[]
no_of_devices = 0
devicelistflag = 0
nodelist = {}

devicepackets=queue.Queue()
mqttpackets = queue.Queue()
devicecommandid=queue.Queue()

def GetgatewayId():
    PORT_XB = '/dev/serial0'# Device port address
    BAUD_RATE_XB = 9600# Device Baud_rate 

    ser_xb1 = serial.Serial(PORT_XB, BAUD_RATE_XB)
    zb1 = ZigBee(ser_xb1)
    zb1.send("at",command='SH')
    response=zb1.wait_read_frame()
    sh=response['parameter']
    zb1.send("at",command='SL')
    response=zb1.wait_read_frame()
    sl=response['parameter']
    #sh=sh.encode('hex')
    #sl=sl.encode('hex')
    sh=binascii.hexlify(sh)
    sl=binascii.hexlify(sl)
    GatewayID=sh+sl
    #Global.myMAC = GatewayID
    GatewayID=GatewayID.upper()
    print ("Gateway ID:",GatewayID)

    ser_xb1.close()
    return GatewayID

def TimeToSend():

    Global.timetosendflag = False
    Global.livestaticcount = 0

if __name__ == "__main__":

    try:

        print ("version 0.l")
        pcf8563 = SDL_PCF8563.SDL_PCF8563(1, 0x51)
        pcf8563.write_now()
        
        Global.myMAC = GetgatewayId()
        Global.mac_Dict = OrderedDict()
        Global.sno_Dict = OrderedDict()
        Global.timetosendflag = False
        try:
            config = open("config.txt", "r")
            username1 =  config.readline()  # type:
            username = username1.strip()
            password1 = config.readline()
            password = password1.strip()
            config.close()
            
            f1 = open("device_list.txt", "r")
            for data in f1.readlines():
                data1 = data.strip()
                data2 = data1.split('.')[0]
                data3 = data1.split('.')[1]
                # print data2[1]
                nodelist[data2]=data3
            f1.close()
        
            Global.DeviceReg = 1
            MAC_DICT = OrderedDict()
            MAC_DICT=nodelist
    
            if not len(MAC_DICT):
                print ("No Device Registration")
                Global.DeviceReg = 0
                raise exception

            else:
                Global.DeviceReg = 1
               #print (MAC_DICT)
                for Device_mac,Device_no in MAC_DICT.items():
                    Global.sno_Dict.update([(Device_mac,Device_no)])
                    Global.mac_Dict.update([(Device_no,Device_mac)])
                print (Global.sno_Dict)
            #print (Global.mac_Dict)
            

        except Exception as err:
            print('Handling run-time error:', err)
        finally:
            pass

        print(" Mqtt Client thread!")
        # Setup a MQTT client
        MqttClient = IOT.MqttThreadedClient(mqttpackets,devicepackets,devicecommandid,MAC_DICT)
        MqttClient.setDaemon(True)
        MqttClient.start()
        
        
        print(" Live Timer thread! ")
        t = Livetimer.TimerClass(10, TimeToSend)
        t.start()
        
        print(" Xbee Server thread!")
        # Setup a MQTT client
        XbeeServer = XbeeDevice.XbeeThreadedServer(mqttpackets,devicepackets,devicecommandid,MAC_DICT)
        time.sleep(2)
        #Global.timetosendflag = True
        XbeeServer.run()



    except (KeyboardInterrupt, SystemExit):
        print("(main) Exception detected")
        #Meshserver.stopserver()
        #TCPCmdParser.stopparser()
    while 1:
        pass