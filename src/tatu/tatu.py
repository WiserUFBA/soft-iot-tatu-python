import paho.mqtt.client as pub
import sensors
import json

#You don't need to change this file. Just change sensors.py and config.json

from time import sleep


procs = []
pub_client = pub.Client(pub.CallbackAPIVersion.VERSION1, client_id='', clean_session=True,protocol=pub.MQTTv31)

class virtualSensor():
    def __init__(self, idP, deviceName, sensorName, sensorsList, met, topic, topicError, pub_client, collectTime, publishTime):
        self.processID = idP
        self.deviceName = deviceName
        self.sensorName = sensorName
        self.sensorsList = sensorsList
        self.met = met
        self.topic = topic
        self.topicError = topicError
        self.pub_client = pub_client
        self.publishTime = publishTime
        self.collectTime = collectTime
        self.run()
    def run(self):
        print ("Starting virtual sensor " + self.processID)

        if (self.met == "EVENT"):
            self.buildEventAnwserDevice()
        elif (self.met == "GET"):
        	self.buildGetAnwserDevice()
        elif (self.met == "FLOW"):
            self.buildFlowAnwserDevice()
        
        print ("Stopping process " + self.processID)


    def buildFlowAnwserDevice(self):
        # Request: {"method": "FLOW", "sensor": "sensorName", "time":{"collect":collectTime,"publish":publishTime}}
        t = 0
        try:
            if not self.sensorsList:
                raise Exception("No sensors")

            for x in self.sensorsList:
                locals()[x["name"]] = []
            
            while True:

                for i in self.sensorsList:
                    sensorName=i["name"]
                    methodFLOW = getattr(sensors, sensorName)
                    retrieved = locals()[i["name"]]
                    retrieved.append(str(methodFLOW()))
					
                t = t + self.collectTime
                arrayValues = []

                if (t >= self.publishTime):
                    header = {"method":"FLOW", "device":self.deviceName, "name":self.sensorName, "time":{"collect":self.collectTime,"publish":self.publishTime}}
                    
                    for y in self.sensorsList:
                        sensorValues = {y["name"]:locals()[y["name"]]}
                        arrayValues.append(sensorValues)
                        locals()[y["name"]] = []
            
                    payload = {"sensors":arrayValues}
              
                    responseModel = {"header":header, "payload":payload}
                    response = json.dumps(responseModel)
                    self.pub_client.publish(self.topic, response)
                    t = 0
                    arrayValues = []

                sleep(self.collectTime)
        except:
            errorMessage = "There is no Sensor"
            #errorMessage = "There is no " + sensorName + " sensor in device " + deviceName
            errorNumber = 1
            responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
            response = json.dumps(responseModel)
            self.pub_client.publish(self.topicError, response)


#{"sensors":[{"humiditySensor":["50","47"]},{"temperatureSensor":["28","29"]}]}


    #TODO: verify self. in params
    def buildEventAnwserDevice(self):
        # Request: {"method":"EVENT", "sensor":"sensorName", "time":{"collect":collectTime}}
         
        try:
            arrayValues = []
            retrieved = []
            header = {"method":"EVENT", "device":self.deviceName, "name":self.sensorName, "time":{"collect":self.collectTime,"publish":self.publishTime}}
            methodEvent = getattr(sensors, self.sensorName)
            value = methodEvent()
            retrieved.append(str(value))
            #retrieved.append(value)
            sensorValues = {self.sensorName:retrieved}
            arrayValues.append(sensorValues)
            payload = {"sensors":arrayValues}
            responseModel = {"header":header, "payload":payload}
            response = json.dumps(responseModel)
            self.pub_client.publish(self.topic, response)
            while True:
                sleep(self.collectTime)
                self.publishTime = self.publishTime + self.collectTime
                aux = methodEvent()
                if aux!=value:
                    arrayValues = []
                    retrieved = []
                    header = {"method":"EVENT", "device":self.deviceName, "name":self.sensorName, "time":{"collect":self.collectTime,"publish":self.publishTime}}
                    value = aux
                    retrieved.append(str(value))
                    #retrieved.append(value)
                    sensorValues = {self.sensorName:retrieved}
                    arrayValues.append(sensorValues)
                    payload = {"sensors":arrayValues}
                    responseModel = {"header":header, "payload":payload}
                    response = json.dumps(responseModel)
                    self.pub_client.publish(self.topic, response)
        except:
            errorMessage = "There is no " + self.sensorName + " sensor in device " + self.deviceName
            errorNumber = 1
            responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
            response = json.dumps(responseModel)
            self.pub_client.publish(self.topicError, response)
            
    
    def buildGetAnwserDevice(self):
        # Request: {"method": "GET", "sensor": "sensorName"}
        try:
            if not self.sensorsList:
                raise Exception("No deviecs")
            
            for x in self.sensorsList:
                locals()[x["name"]] = []
            
            for i in self.sensorsList:
                sensorName= i["name"]
                methodGet = getattr(sensors, sensorName)
                retrieved = locals()[i["name"]]
                retrieved.append(str(methodGet()))
					
            print("methodGET")

            arrayValues = []

            header = {"method":"GET", "device":self.deviceName, "name":self.sensorName}
                    
            for y in self.sensorsList:
                sensorValues = {y["name"]:locals()[y["name"]]}
                arrayValues.append(sensorValues)
                locals()[y["name"]] = []
            
            payload = {"sensors":arrayValues}
            
            responseModel = {"header":header, "payload":payload}
            response = json.dumps(responseModel)
            self.pub_client.publish(self.topic, response)

        except:
            errorMessage = "There is no " + self.sensorName + " sensor in device " + self.deviceName
            errorNumber = 1
            responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
            response = json.dumps(responseModel)
            pub_client.publish(self.topicError, response)
 

 
    #TODO: verify self. in params
    def buildPostAnwserDevice(self):
        try:
            methodPost = getattr(sensors, self.sensorName)
            methodPost(value)

            #Request: {"method":"POST", "sensor":"sensorName", "value":value}
            responseModel = {"code":"POST","method":"POST", "sensor":self.sensorName, "value":value}
            response = json.dumps(responseModel)
            self.pub_client.publish(self.topic, response)
        except:
            errorMessage = "There is no " + self.sensorName + " sensor in device " + self.deviceName
            errorNumber = 1
            responseModel = {"code":"ERROR", "number":errorNumber, "message":errorMessage}
            response = json.dumps(responseModel)
            self.pub_client.publish(self.topicError, response)



def on_disconnect(mqttc, obj, msg):
    print("disconnected tatu!")

def main(data, msg):
    mqttBroker = data["mqttBroker"]
    mqttPort = data["mqttPort"]
    mqttUsername = data["mqttUsername"]
    mqttPassword = data["mqttPassword"]
    deviceName = data["deviceName"]
    topic = data["topicPrefix"] + deviceName + data["topicRes"]
    topicError = data["topicPrefix"] + deviceName + data["topicErr"]
    sensorsList = data["sensors"]

	
    msgJson = json.loads(msg.payload)
    sensorName = msgJson["sensor"]
    met = msgJson["method"]

    found = 0
    
    if (sensorName!=deviceName):
        for sen in sensorsList:
            if (sen["name"]==sensorName):
                sensorsList = []
                sensorsList.append(sen)
                found = 1
                break
        if not found:
            sensorsList = []
    
    print("-------------------------------------------------")
    print("| Topic: " + str(msg.topic))
    print("| Message: " + str(msg.payload))
    print("-------------------------------------------------")
    idP = met + "_" + deviceName + "_" + sensorName
    pub_client.user_data_set(data)
    pub_client.on_disconnect = on_disconnect
    pub_client.connect(mqttBroker, mqttPort, 60)
    
    
    if (met=="POST"):
        pass
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

        sensor = virtualSensor(idP, deviceName, sensorName, sensorsList, met, topic, topicError, pub_client, collectTime, publishTime)
