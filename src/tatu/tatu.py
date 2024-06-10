import paho.mqtt.client as pub
import sensors
import json
import multiprocessing

#You don't need to change this file. Just change sensors.py and config.json

from time import sleep


procs = []


class sensorProcess (multiprocessing.Process):
    def __init__(self, idP, deviceName, sensorName, met, topic, topicError, pub_client, collectTime, publishTime):
        multiprocessing.Process.__init__(self)
        self.processID = idP
        self.deviceName = deviceName
        self.sensorName = sensorName
        self.met = met
        self.topic = topic
        self.topicError = topicError
        self.pub_client = pub_client
        self.publishTime = publishTime
        self.collectTime = collectTime
    def run(self):
        print ("Starting process " + self.processID)

        if (self.met == "EVENT"):
            buildEventAnwserDevice(self.deviceName, self.sensorName, self.topic, self.topicError, self.pub_client, self.collectTime, self.publishTime)
        elif (self.met == "GET"):
        	buildGetAnwserDevice(self.deviceName, self.sensorName, self.topic, self.topicError, self.pub_client)
        elif (self.met == "FLOW"):
            buildFlowAnwserDevice(self.deviceName, self.sensorName, self.topic, self.topicError, self.pub_client, self.collectTime, self.publishTime)
        
        print ("Stopping process " + self.processID)

class actuatorProcess (multiprocessing.Process):
    def __init__(self, idP, deviceName, sensorName, met, topic, topicError, pub_client, value):
        multiprocessing.Process.__init__(self)
        self.processID = idP
        self.deviceName = deviceName
        self.sensorName = sensorName
        self.met = met
        self.topic = topic
        self.topicError = topicError
        self.pub_client = pub_client
        self.value = value

    def run(self):
        print ("Starting process " + self.processID)

        if (self.met == "POST"):
            buildPostAnwserDevice(self.deviceName, self.sensorName, self.topic, self.topicError, self.pub_client, self.value)
        
        print ("Stopping process " + self.processID)
 
def buildFlowAnwserDevice(deviceName, sensorName, topic, topicError, pub_client, collectTime, publishTime):
    value = ""
    t = 0
    try:
        methodFLOW = getattr(sensors, sensorName)
        listValues = []
        while True:
            listValues.append(str(methodFLOW()))
            t = t + collectTime
            if (t >= publishTime):
                #Request: {"method":"FLOW", "sensor":"sensorName", "time":{"collect":collectTime,"publish":publishTime}}
                responseModel = {"CODE":"POST","METHOD":"FLOW","HEADER":{"NAME":deviceName},"BODY":{sensorName:listValues,"FLOW":{"collect":(collectTime),"publish":(publishTime)}}}
                response = json.dumps(responseModel)
                pub_client.publish(topic, response)
                t = 0
                listValues = []
            sleep(collectTime)
    except:
        errorMessage = "There is no " + sensorName + " sensor in device " + deviceName
        errorNumber = 1
        responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
        response = json.dumps(responseModel)
        pub_client.publish(topicError, response)


def buildEventAnwserDevice(deviceName, sensorName, topic, topicError, pub_client, collectTime, publishTime):
    try:
        methodEvent = getattr(sensors, sensorName)
        value = methodEvent()
        #Request: {"method":"EVENT", "sensor":"sensorName", "time":{"collect":collectTime}}
        responseModel = {"CODE":"POST","METHOD":"EVENT","HEADER":{"NAME":deviceName},"BODY":{sensorName:value,"EVENT":{"collect":(collectTime),"publish":(publishTime)}}}
        response = json.dumps(responseModel)
        pub_client.publish(topic, response)

        while True:
            sleep(collectTime)
            publishTime = publishTime + collectTime
            aux = methodEvent()
            if aux!=value:
                value = aux
                #Request: {"method":"EVENT", "sensor":"deviceName", "time":{"collect":collectTime}}
                responseModel = {"CODE":"POST","METHOD":"EVENT","HEADER":{"NAME":deviceName},"BODY":{sensorName:value,"EVENT":{"collect":(collectTime),"publish":(publishTime)}}}
                response = json.dumps(responseModel)
                pub_client.publish(topic, response)
    except:
        errorMessage = "There is no " + sensorName + " sensor in device " + deviceName
        errorNumber = 1
        responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
        response = json.dumps(responseModel)
        pub_client.publish(topicError, response)


def buildGetAnwserDevice(deviceName, sensorName, topic, topicError, pub_client):
    try:
        methodGet = getattr(sensors, sensorName)
        value = methodGet()

        #Request: {"method":"GET", "sensor":"sensorName"}
        responseModel = {'CODE':'POST','METHOD':'GET','HEADER':{'NAME':deviceName},'BODY':{sensorName:value}}
        response = json.dumps(responseModel)

        pub_client.publish(topic, response)
    except:
        errorMessage = "There is no " + sensorName + " sensor in device " + deviceName
        errorNumber = 1
        responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
        response = json.dumps(responseModel)
        pub_client.publish(topicError, response)

def buildPostAnwserDevice(deviceName, sensorName, topic, topicError, pub_client, value):
    try:
        #p = "__" + sensorName + "__"
        methodPost = getattr(sensors, sensorName)
        methodPost(value)

        #Request: {"method":"POST", "sensor":"sensorName", "value":value}
        responseModel = {"code":"POST","method":"POST", "sensor":sensorName, "value":value}
        response = json.dumps(responseModel)
        pub_client.publish(topic, response)
    except:
        errorMessage = "There is no " + sensorName + " sensor in device " + deviceName
        errorNumber = 1
        responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
        response = json.dumps(responseModel)
        pub_client.publish(topicError, response)

#def status ():
#{"method":"EVENT", "sensor":"soundSensor", "status":False}
#{"method":"STOP", "target": "EVENT", "sensor":"soundSensor"}

def on_disconnect(mqttc, obj, rc):
    print("disconnected tatu!")

def main(data, msg):
    mqttBroker = data["mqttBroker"]
    mqttPort = data["mqttPort"]
    mqttUsername = data["mqttUsername"]
    mqttPassword = data["mqttPassword"]
    deviceName = data["deviceName"]
    topic = data["topicPrefix"] + deviceName + data["topicRes"]
    topicError = data["topicPrefix"] + deviceName + data["topicErr"]

    msgJson = json.loads(msg.payload)
    sensorName = msgJson["sensor"]
    met = msgJson["method"]

    print("-------------------------------------------------")
    print("| Topic:" + str(msg.topic))
    print("| Message: " + str(msg.payload))
    print("-------------------------------------------------")
    idP = met + "_" + deviceName + "_" + sensorName
    pub_client = pub.Client(idP)
    pub_client.username_pw_set(mqttUsername, mqttPassword)
    pub_client.user_data_set(data)
    pub_client.on_disconnect = on_disconnect
    pub_client.connect(mqttBroker, mqttPort, 60)
    
    if (met=="STOP"):
        #{"method":"STOP", "target": "EVENT", "sensor":"soundSensor"}
        idP = msgJson["target"] + "_" + deviceName + "_" + sensorName
        stopped = False
        for proc in procs:
            if (proc.processID==idP):
                print ("Stopping process " + proc.processID)
                procs.remove(proc)
                proc.terminate()
                stopped = True
                break
        if not stopped:
            #error in json to /ERR
            errorMessage = "There is no running process named " + idP
            errorNumber = 2
            responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
            response = json.dumps(responseModel)
            pub_client.publish(topicError, response)
    elif (met=="POST"):
        #{"method":"POST", "sensor":"sensorName", "value":value}
        value = msgJson["value"]
        proc = actuatorProcess(idP, deviceName, sensorName, met, topic, topicError, pub_client, value)
        procs.append(proc)
        proc.start()
    else:
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

        proc = sensorProcess(idP, deviceName, sensorName, met, topic, topicError, pub_client, collectTime, publishTime)
        procs.append(proc)
        proc.start()


