import paho.mqtt.client as mqtt
import json
import tatu

#You don't need to change this file. Just change sensors.py and config.json

topicPrefix = "dev/"

def on_connect(mqttc, obj, flags, rc):
    topic = topicPrefix + obj["name"] + "/#"
    print("Topic device subscribed: " + topic)
    mqttc.subscribe(topic)

def on_message(mqttc, obj, msg):
	#{"BODY": {"humiditySensor": 51}, "HEADER": {"NAME": "ufbaino01"}, "CODE": "POST", "METHOD": "GET"}
    if "RES" not in msg.topic:
    	tatu.main(obj, msg)

with open('config.json') as f:
  data = json.load(f)

mqtt_url = data["mqtt.url"]
mqtt_port = data["mqtt.port"]
mqtt_username = data["mqtt.username"]
mqtt_password = data["mqtt.password"]
name = data["name"]


sub_client = mqtt.Client(name + "_sub")

sub_client.username_pw_set(mqtt_username, mqtt_password)
sub_client.on_connect = on_connect
sub_client.on_message = on_message
sub_client.user_data_set(data)
sub_client.connect(mqtt_url, mqtt_port, 60)

sub_client.loop_forever()
