#   Copyright 2018-2019 AyKa Technologies


from xbee import ZigBee
import queue
import time
import datetime
import serial
import pprint
import logging
import threading
import mqttcloud as IOT
import json
import logging
from threading import Timer, Thread, Event
from configparser import *
from uuid import getnode as get_mac
import mqttcloud
from collections import OrderedDict
import pickle
import Global
import filelogger
import binascii
import codecs
import base64
from json import loads, dumps

START_CHAR  = 0x01
STOP_CHAR   = 0x04
DEVICE_ID   = 255
DELIMITER_1 = 0x02
DELIMITER_2 = 0x03
CRC         = 2


""" 
    In XbeeThreadedServer Class the responses from devices to the Gateway will be carriedout without losing any data.
    And also sends the commends to all devices from gateway which are received from cloud (server).
    In this class what is the data coming from devies to gateway are put in a queue so that no data will be lostwhile receiving from gateway side.
    
"""

class XbeeThreadedServer(object):
    def __init__(self, mqttpackets,devicepackets,devicecommandid,MAC_DICT, **kwds):

        try:
            PORT_XB = '/dev/serial0'
            BAUD_RATE_XB = 9600
            #time.sleep(5)
            self.ser_xb = serial.Serial(PORT_XB, BAUD_RATE_XB)
            self.zb = ZigBee(self.ser_xb, callback=self.device_message_received)	# created an object zb
            self.devicepackets = queue.Queue()
            self.mqttsendpackets = mqttpackets
            self.devicesendpackets = devicepackets
            self.devicecommandid = devicecommandid
            self.MAC_DICT=MAC_DICT
            self.xbeestopflag = 0
        except Exception as e:
            print (e)
        finally:
            pass

    def formatLongAddr(self,addrLong):
        pretty_value = ''.join("{:02X}".format((c)) for c in addrLong)
        #print('formatLongAddr()> formated AddrLong: %s' % (pretty_value))
        return pretty_value

    def formatShortAddr(self,addrShort):

        pretty_value = ':'.join("{:02X}".format(ord(c)) for c in addrShort)
        #print('formatShortAddr()> formated AddrShort: %s' % (prettsy_value))
        return pretty_value

    def device_message_received(self,data):
        #print("Data received from Node")
        #print(str(data))
        self.devicepackets.put((data), block=False)
        #print (type(data['source_addr_long']))
        #print(str(data))

    def sendPacket(self,where, what):

        #UNKNOWN = b'\xff\xfe'
        #where = b'\x00\x13\xa2\x00\x41\xBF\xB5\x24'
        #what = b'\xff\xfe'
        #print("sending xbee data")
        self.zb.send('tx',
                        dest_addr_long = where,
                       data = what)
        #print('sendPacket()> Data: '+ str(binascii.hexlify(what)))
        #print('sendPacket()> Data sent to: '+ str(binascii.hexlify(where)) )

    def handlePacket(self,data):


        global xbeeindex
        global macData
        global devicedata
        #global mac_Dict
        #global MAC_DICT
        global sno_Dict
        global commandID
        global command
        global current_time
        global livepackets_list
        global livedatapacketindex


        Time=time.time()# Unix time stamp
        current_time=int(Time)# Converting the timesatmp into 'int'
        
        try:

            if data['id'] == 'rx':
                #print("Data packet from Node")
                Response_Packet={}
                Response = (data['rf_data'])
                print(Response)
                macData = self.formatLongAddr(data['source_addr_long'])
                #macData=str(macData)
                res = ''.join("{:02X}".format((c)) for c in Response)
                #print (res)
                res1=binascii.hexlify(Response)
                #print (res1)
                resp=Response[4:8]  # Slicing the data to check the command type
                resp=resp.decode('utf-8')
                val= bytearray.fromhex(str(Response[9]))
                print (val)
                
                #print("This is End Node Data")
                
                Response_Packet["DID"]=str(macData)
                Response_Packet["CMD"]=  resp

                #print (Response_Packet)
                if (resp =='1111'):
                    Response_Packet["VALUES"]= val #str(Response[9])
                else:
                    Response_Packet["VALUES"]= (Response[9:-2]).decode ('utf-8')

                Response_Packet=json.dumps(Response_Packet)
                print (Response_Packet)

                self.devicesendpackets.put(Response_Packet)
                self.devicesendpackets.task_done()


            if data['id'] == 'tx_status':
                #print("Status Packet from Node")
                print('handlePacket()> deliver_status: ' + str(binascii.hexlify(data['deliver_status'])))
                if (((binascii.hexlify(data['deliver_status']))) == b'24'):
                    print('MAC Address Not Found ')

        except Exception as e:
            print (e)

        finally:
            pass

    def run(self):
        #global mac_Dict
        global sno_Dict
        #global newmac_Dict
        global devicelistflag
        Global.livestaticcount=0
        
        try:
            

        # Extract the first item from the command queue
            while not(self.xbeestopflag):
                #print(" Xbee Runing! ")
                if not self.mqttsendpackets.empty():
                    data_to_send = self.mqttsendpackets.get()
                    json = loads(data_to_send) #json['DID']
                    macaddress= bytes.fromhex(json['DID'])
                    values = json['VALUES']
                    print(macaddress)
                    print(values)
                    #print(type(macaddress))
                    #macaddress = str(macaddress)
                    if len(json) < 3:
                        values = CRC
                    else:
                        values = "%s,%d" % (json['VALUES'], 2)
                        
                    #print(values)
                    enc_data = "%c%02X%c%s%c%s%c" % (START_CHAR, DEVICE_ID, DELIMITER_1, json['CMD'], DELIMITER_2, values, STOP_CHAR)
                    #print (enc_data)
                    self.sendPacket(macaddress,enc_data)
 

                if not self.devicepackets.empty():
                    #if Global.DeviceReg == 1:
                    #print ("new device found")

                    newPacket = self.devicepackets.get()
                    self.handlePacket(newPacket)

                if Global.DeviceReg == 1:
                    if Global.timetosendflag == True:
                        maclist = list((Global.mac_Dict.keys()))
                        print ((maclist))
                        macdevicelen = len(maclist)

                        data = {}    

        
                        #pkt=pkt.decode("hex")
                        #pkt=binascii.hexlify(pkt)
                        #pkt = [binary.fromhex(_).decode('utf-8') for _ in pkt]
                        #pkt = bytearray.fromhex(pkt)

                        

                        #for key,value in Global.mac_Dict.items():

                        key = maclist[Global.livestaticcount]
                        print (key)
                        print (type(key))
                        macaddress= key
                        macaddress= bytes.fromhex(key)
                        #macaddress= codecs.decode(key,'hex')
                        #macaddress = ''.join("{:02X}".format(ord(c)) for c in macaddress)
                        #macaddress = binascii.hexlify(macaddress)
                        #macaddress = bytearray(macaddress)
                        #macaddress = base64.b64decode(key)
                        print ("*********")
                        print (macaddress)
                        print (type(macaddress))
                        print ("*********")
                        
                        #data["DID"] = str(macaddress)
                        data["CMD"] = '101C'
                        #if values != '2':
                        #data["VALUES"] = '3'
                        #data_to_send = '{"DID":"%s","CMD":"%s","VALUES":"%s"}' % (did, cmd, values)        
                        data_to_send = dumps(data)
                        print (data_to_send)
                        json = loads(data_to_send)
                        
                        if len(json) < 3:
                            values = CRC
                        else:
                            values = "%s,%d" % (json['VALUES'], 2)
                            
                        #print(values)
                        enc_data = "%c%02X%c%s%c%s%c" % (START_CHAR, DEVICE_ID, DELIMITER_1, json['CMD'], DELIMITER_2, values, STOP_CHAR)
                        #print(enc_data)
                        #enc_data_base_64 = base64.b64encode(bytes(enc_data, 'utf-8'))
                        #enc_data_base_64 = bytes.fromhex(enc_data)
                        #enc_data_base_64 =binascii.hexlify(enc_data)
                        #pkt = enc_data_base_64
                        pkt = enc_data
                        print ('sending paket to Xbee')
                        print (pkt)
                        self.sendPacket(macaddress,pkt)
                        Global.livestaticcount += 1
                        
                        time.sleep(1)

                        if Global.livestaticcount == macdevicelen:
                            Global.livestaticcount = 0
                            Global.timetosendflag = False
                            
        except Exception as e:
            print (e)
        finally:
            pass


