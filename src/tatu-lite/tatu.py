import paho.mqtt.client as pub
import sensors
import json
import threading

#You don't need to change this file. Just change sensors.py and config.json

from time import sleep

topicPrefix = "dev/"


class minhaThread (threading.Thread):
    def __init__(self, deviceName, sensorName, met, topic, pub_client, collectTime, publishTime):
        threading.Thread.__init__(self)
        self.threadID = (met + "_" + deviceName + "_" + sensorName)
        self.deviceName = deviceName
        self.sensorName = sensorName
        self.met = met
        self.topic = topic
        self.pub_client = pub_client
        self.publishTime = publishTime/1000
        self.collectTime = collectTime/1000

    def run(self):
        print ("Starting thread " + self.threadID)

        if (self.met == "FLOW"):
        	buildFlowAnwserDevice(self.deviceName, self.sensorName, self.topic, self.pub_client, self.collectTime, self.publishTime)
        elif (self.met == "EVENT"):
        	buildEventAnwserDevice(self.deviceName, self.sensorName, self.topic, self.pub_client, self.collectTime, self.publishTime)
        elif (self.met == "GET"):
        	buildGetAnwserDevice(self.deviceName, self.sensorName, self.topic, self.pub_client)
        
        print ("Stopping thread " + self.threadID)
 
def buildFlowAnwserDevice(deviceName, sensorName, topic, pub_client, collectTime, publishTime):
    value = ""
    t = 0
    try:
        methodFLOW = getattr(sensors, sensorName)
        listValues = []
        while True:
            listValues.append(str(methodFLOW()))
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
        print("There is no " + sensorName + " sensor in device " + deviceName)


def buildEventAnwserDevice(deviceName, sensorName, topic, pub_client, collectTime, publishTime):
#EVENT VALUE sensorName {"collect":10000}
#{"CODE":"POST","METHOD":"EVENT","HEADER":{"NAME":"deviceName"},"BODY":{"sensorName":"value"}}
    try:
        methodEvent = getattr(sensors, sensorName)
        value = methodEvent()
        responseModel = {"CODE":"POST","METHOD":"EVENT","HEADER":{"NAME":deviceName},"BODY":{sensorName:value,"EVENT":{"collect":(collectTime*1000),"publish":(publishTime*1000)}}}
        #responseModel = {'CODE':'POST','METHOD':'EVENT','HEADER':{'NAME':deviceName},'BODY':{sensorName:value}}
        response = json.dumps(responseModel)
        pub_client.publish(topic, response)

        while True:
            sleep(collectTime)
            publishTime = publishTime + collectTime
            aux = methodEvent()
            if aux!=value:
                value = aux
                #Request:  #GET VALUE sensorName
                responseModel = {"CODE":"POST","METHOD":"EVENT","HEADER":{"NAME":deviceName},"BODY":{sensorName:value,"EVENT":{"collect":(collectTime*1000),"publish":(publishTime*1000)}}}
                #responseModel = {'CODE':'POST','METHOD':'EVENT','HEADER':{'NAME':deviceName},'BODY':{sensorName:value}}
                response = json.dumps(responseModel)
                pub_client.publish(topic, response)
    except:
        print("There is no " + sensorName + " sensor in device " + deviceName)


def buildGetAnwserDevice(deviceName, sensorName, topic, pub_client):
    try:
        methodGet = getattr(sensors, sensorName)
        value = methodGet()

        #Request:  #GET VALUE sensorName
        responseModel = {'CODE':'POST','METHOD':'GET','HEADER':{'NAME':deviceName},'BODY':{sensorName:value}}
        response = json.dumps(responseModel)

        pub_client.publish(topic, response)
    except:
        print("There is no " + sensorName + " sensor in device " + deviceName)

def main(data, msg):
    #{"method":"GET", "sensor":"soundSensor"}
    #{"method":"FLOW", "sensor":"soundSensor", "time":{"collect":5000,"publish":10000}}
    #{"method":"EVENT", "sensor":"soundSensor", "time":{"collect":5000}}

    mqtt_url = data["mqtt.url"]
    mqtt_port = data["mqtt.port"]
    mqtt_username = data["mqtt.username"]
    mqtt_password = data["mqtt.password"]
    deviceName = data["name"]

    msgJson = json.loads(msg.payload)
    met = msgJson["method"]
    sensorName = msgJson["sensor"]

    pub_client = pub.Client(deviceName + "_" + sensorName + "_" + met)
    pub_client.username_pw_set(mqtt_username, mqtt_password)
    pub_client.user_data_set(data)
    pub_client.connect(mqtt_url, mqtt_port, 60)

    
    print ("-------------------------------------------------")
    print("| Topic:" + str(msg.topic))
    print("| Message: " + str(msg.payload))
    print("-------------------------------------------------")
    topic = topicPrefix + deviceName + "/RES"

    if (met=="GET"):
    	collectTime = 0
    	publishTime = 0
    elif (met=="FLOW"):
        time = msgJson["time"]
        collectTime = time["collect"]
        publishTime = time["publish"]
    elif (met=="EVENT"):
        time = msgJson["time"]
        collectTime = time["collect"]
    	publishTime = 0

    thread = minhaThread(deviceName, sensorName, met, topic, pub_client, collectTime, publishTime)
    thread.start()
       