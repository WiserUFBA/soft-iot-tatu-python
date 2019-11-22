import paho.mqtt.client as mqtt2
import sensors
import json
import threading

#You don't need to change this file. Just change sensors.py and config.json

from time import sleep

topicPrefix = "dev/"


class minhaThread (threading.Thread):
    def __init__(self, deviceName, sensorName, topic, pub_client, collectTime, publishTime, met):
        threading.Thread.__init__(self)
        self.threadID = (met + "_" + deviceName + "_" + sensorName)
        self.deviceName = deviceName
        self.sensorName = sensorName
        self.topic = topic
        self.pub_client = pub_client
        self.publishTime = publishTime/1000
        self.collectTime = collectTime/1000
        self.met = met

    def run(self):
        print ("Starting thread " + self.threadID)

        if (self.met == "FLOW"):
        	buildFlowAnwserDevice(self.deviceName, self.sensorName, self.topic, self.pub_client, self.collectTime, self.publishTime)
        else:
        	buildEvtAnwserDevice(self.deviceName, self.sensorName, self.topic, self.pub_client, self.collectTime, self.publishTime)

        print ("Stopping thread " + self.threadID)
 
def buildFlowAnwserDevice(deviceName, sensorName, topic, pub_client, collectTime, publishTime):
    value = ""
    t = 0
    try:
        method = getattr(sensors, sensorName)
        listValues = []
        while True:
            listValues.append(str(method()))
            t = t + collectTime
            if t >= publishTime:
                #Request: FLOW VALUE sensorName {"collect":collectTime,"publish":publishTime}
                responseModel = {"CODE":"POST","METHOD":"FLOW","HEADER":{"NAME":deviceName},"BODY":{sensorName:listValues,"FLOW":{"collect":(collectTime*1000),"publish":(publishTime*1000)}}}
                response = json.dumps(responseModel)
                pub_client.publish(topic, response)
                t = 0
                listValues = []
            sleep(collectTime)
    except:
        print("There is no " + sensorName + " in this device")


def buildEvtAnwserDevice(deviceName, sensorName, topic, pub_client, collectTime, publishTime):
#EVT VALUE sensorName {"collect":10000}
#{"CODE":"POST","METHOD":"EVT","HEADER":{"NAME":"deviceName"},"BODY":{"sensorName":"value"}}
    try:
        method = getattr(sensors, sensorName)
        value = method()
        responseModel = {"CODE":"POST","METHOD":"EVT","HEADER":{"NAME":deviceName},"BODY":{sensorName:value,"EVT":{"collect":(collectTime*1000),"publish":(publishTime*1000)}}}
        #responseModel = {'CODE':'POST','METHOD':'EVT','HEADER':{'NAME':deviceName},'BODY':{sensorName:value}}
        response = json.dumps(responseModel)
        pub_client.publish(topic, response)

        while True:
            sleep(collectTime)
            publishTime = publishTime + collectTime
            aux = method()
            if aux!=value:
                value = aux
                #Request:  #GET VALUE sensorName
                responseModel = {"CODE":"POST","METHOD":"EVT","HEADER":{"NAME":deviceName},"BODY":{sensorName:value,"EVT":{"collect":(collectTime*1000),"publish":(publishTime*1000)}}}
                #responseModel = {'CODE':'POST','METHOD':'EVT','HEADER':{'NAME':deviceName},'BODY':{sensorName:value}}
                response = json.dumps(responseModel)
                pub_client.publish(topic, response)
    except:
        print("There is no " + sensorName + " in this device")


def buildGetAnwserDevice(deviceName, sensorName, topic, pub_client):
    try:
        method = getattr(sensors, sensorName)
        value = method()

        #Request:  #GET VALUE sensorName
        responseModel = {'CODE':'POST','METHOD':'GET','HEADER':{'NAME':deviceName},'BODY':{sensorName:value}}
        response = json.dumps(responseModel)

        pub_client.publish(topic, response)
    except:
        print("There is no " + sensorName + " in this device")

def main(data, msg):
    mqtt_url = data["mqtt.url"]
    mqtt_port = data["mqtt.port"]
    mqtt_username = data["mqtt.username"]
    mqtt_password = data["mqtt.password"]
    deviceName = data["name"]

    msgList = (str(msg.payload)).split(" ")
    met = msgList[0]
    info = msgList[1]
    sensorName = msgList[2]

    pub_client = mqtt2.Client(deviceName + "_" + sensorName + "_pub")
    pub_client.username_pw_set(mqtt_username, mqtt_password)
    pub_client.user_data_set(data)
    pub_client.connect(mqtt_url, mqtt_port, 60)

    
    print ("-------------------------------------------------")
    print("| Topic:" + str(msg.topic))
    print("| Message: " + str(msg.payload))
    print("-------------------------------------------------")
    topic = topicPrefix + deviceName + "/RES"

    if (met=="GET"):
        buildGetAnwserDevice(deviceName, sensorName, topic, pub_client)
    elif ((met=="FLOW") or (met=="EVT")):
        try:
            msgConf = (str(msgList[3]) + str(msgList[4]))
        except:
            msgConf = (str(msgList[3]))

        config = json.loads(msgConf)
        if (met=="FLOW"):
            collectTime = config["collect"]
            publishTime = config["publish"]
        else:
            collectTime = config["collect"]
            publishTime = 0
    	
        thread = minhaThread(deviceName, sensorName, topic, pub_client, collectTime, publishTime, met)
        thread.start()
   