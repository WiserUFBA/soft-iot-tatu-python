import paho.mqtt.client as mqtt
import json

from time import sleep
from multiprocessing import Process
#You don't need to change this file. Just change sensors.py and config.json


#process list
procs=[]

#create new virtual sensors instances 
class tatu_process(Process):
    def __init__(self,obj,msg,process_id):
        Process.__init__(self)
        self.obj=obj
        self.msg=msg
        self.process_id=process_id
        
    def run(self):
        import tatu
        tatu.main(self.obj, self.msg)

def on_connect(mqttc, obj, flags, rc):
    topic = obj["topicPrefix"] + obj["deviceName"] + obj["topicReq"] + "/#"
    mqttc.subscribe(topic)
    print("Device's sensors:")
    for sensor in obj['sensors']:
    	print ("\t" + sensor['name'])
    print("Topic device subscribed: " + topic)

def on_message(mqttc, obj, msg):
    if obj["topicReq"] in msg.topic:
        tatu_msg=json.loads(msg.payload)
        if(tatu_msg['method']=='STOP'):
            stop_sensor(obj,tatu_msg)
        else:
            init_sensor(obj,tatu_msg,msg)
        

def on_disconnect(mqttc, obj, rc):
	print("disconnected!")
	exit()

def init_sensor(obj,tatu_msg,msg):
    process_id=tatu_msg['method']+'_'+obj['deviceName']+'_'+tatu_msg['sensor']
    p = tatu_process(obj,msg,process_id)
    procs.append(p)
    p.start()

def stop_sensor(obj,tatu_msg):
    process_id=tatu_msg['target']+'_'+obj['deviceName']+'_'+tatu_msg['sensor']
    for proc in procs:
        if (proc.process_id==process_id):
            print ("Stopping process " + proc.process_id)
            procs.remove(proc)
            proc.terminate()


while True:
	with open('config.json') as f:
		data = json.load(f)
	
	mqttBroker = data["mqttBroker"]
	mqttPort = data["mqttPort"]
	mqttUsername = data["mqttUsername"]
	mqttPassword = data["mqttPassword"]
	deviceName = data["deviceName"]
    
    #for 2.0 and newer versions of paho-mqtt use that:
	sub_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, deviceName + "_sub", protocol=mqtt.MQTTv31)
    #see changes in: https://github.com/eclipse/paho.mqtt.python/blob/master/docs/migrations.rst
    
    #for 1.x versions of paho-mqtt use that: 
    #sub_client = mqtt.Client(deviceName + "_sub", protocol=mqtt.MQTTv31)
    

	sub_client.username_pw_set(mqttUsername, mqttPassword)
	sub_client.user_data_set(data)
	sub_client.on_connect = on_connect
	sub_client.on_message = on_message
	sub_client.on_disconnect = on_disconnect

	try:
		sub_client.connect(mqttBroker, mqttPort, 60)
		sub_client.loop_forever()
	except:
		print ("Broker unreachable on " + mqttBroker + " URL!")
		sleep(5)
