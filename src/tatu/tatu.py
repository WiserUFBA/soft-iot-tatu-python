import paho.mqtt.client as pub
import sensors
import json
import traceback

# You don't need to change this file. Just change sensors.py and config.json


class virtualSensor():
    def __init__(self, idP, deviceName, sensorName, sensorsList, met, topic,
                 topicError, pub_client, collectTime, publishTime, stop_event,
                 post_value=None):
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
        self.stop_event = stop_event
        self.post_value = post_value

    def run(self):
        print("Starting virtual sensor " + self.processID)

        if self.met == "EVENT":
            self.buildEventAnswerDevice()
        elif self.met == "GET":
            self.buildGetAnswerDevice()
        elif self.met == "FLOW":
            self.buildFlowAnswerDevice()
        elif self.met == "POST":
            self.buildPostAnswerDevice()

        print("Stopping process " + self.processID)

    def buildFlowAnswerDevice(self):
        # Request: {"method": "FLOW", "sensor": "sensorName", "time":{"collect":collectTime,"publish":publishTime}}
        t = 0
        try:
            if not self.sensorsList:
                raise Exception("No sensors")

            sensor_dict = {}
            for x in self.sensorsList:
                sensor_dict[x["name"]] = []

            while not self.stop_event.is_set():
                for i in self.sensorsList:
                    sensorName = i["name"]
                    method_fn = getattr(sensors, sensorName)
                    sensor_dict[sensorName].append(method_fn())

                t = t + self.collectTime

                if t >= self.publishTime:
                    header = {
                        "method": "FLOW",
                        "device": self.deviceName,
                        "sensor": self.sensorName,
                        "time": {"collect": self.collectTime, "publish": self.publishTime},
                    }
                    array_values = [
                        {name: list(values)} for name, values in sensor_dict.items()
                    ]
                    payload = {"sensors": array_values}
                    response = json.dumps({"header": header, "payload": payload})
                    self.pub_client.publish(self.topic, response)
                    self.pub_client.loop(timeout=1.0)
                    t = 0
                    for name in sensor_dict:
                        sensor_dict[name] = []

                # wait() returns True if stop was signalled — exits immediately on STOP
                if self.stop_event.wait(timeout=self.collectTime):
                    break

        except Exception:
            print(traceback.format_exc())
            error = json.dumps({"code": "ERROR", "number": 1, "message": "Error reading sensor"})
            self.pub_client.publish(self.topicError, error)
            self.pub_client.loop(timeout=1.0)

    def buildEventAnswerDevice(self):
        # Request: {"method":"EVENT", "sensor":"sensorName", "time":{"collect":collectTime}}
        try:
            method_fn = getattr(sensors, self.sensorName)
            value = method_fn()
            retrieved = [value]
            header = {
                "method": "EVENT",
                "device": self.deviceName,
                "sensor": self.sensorName,
                "time": {"collect": self.collectTime, "publish": self.publishTime},
            }
            payload = {"sensors": [{self.sensorName: retrieved}]}
            response = json.dumps({"header": header, "payload": payload})
            self.pub_client.publish(self.topic, response)
            self.pub_client.loop(timeout=1.0)

            # wait() returns True if stop was signalled; loop while it times out
            while not self.stop_event.wait(timeout=self.collectTime):
                aux = method_fn()
                if aux != value:
                    value = aux
                    retrieved = [value]
                    payload = {"sensors": [{self.sensorName: retrieved}]}
                    response = json.dumps({"header": header, "payload": payload})
                    self.pub_client.publish(self.topic, response)
                    self.pub_client.loop(timeout=1.0)

        except Exception:
            print(traceback.format_exc())
            error = json.dumps({
                "code": "ERROR",
                "number": 1,
                "message": f"There is no {self.sensorName} sensor in device {self.deviceName}",
            })
            self.pub_client.publish(self.topicError, error)
            self.pub_client.loop(timeout=1.0)

    def buildGetAnswerDevice(self):
        # Request: {"method": "GET", "sensor": "sensorName"}
        try:
            if not self.sensorsList:
                raise Exception("No sensors")

            sensor_dict = {}
            for x in self.sensorsList:
                sensor_dict[x["name"]] = []

            for i in self.sensorsList:
                sensorName = i["name"]
                method_fn = getattr(sensors, sensorName)
                sensor_dict[sensorName].append(method_fn())

            print("methodGET")

            header = {"method": "GET", "device": self.deviceName, "sensor": self.sensorName}
            array_values = [{name: list(values)} for name, values in sensor_dict.items()]
            payload = {"sensors": array_values}
            response = json.dumps({"header": header, "payload": payload})
            self.pub_client.publish(self.topic, response)
            self.pub_client.loop(timeout=1.0)

        except Exception:
            print(traceback.format_exc())
            error = json.dumps({
                "code": "ERROR",
                "number": 1,
                "message": f"There is no {self.sensorName} sensor in device {self.deviceName}",
            })
            self.pub_client.publish(self.topicError, error)
            self.pub_client.loop(timeout=1.0)

    def buildPostAnswerDevice(self):
        # Request: {"method":"POST", "sensor":"sensorName", "value":value}
        try:
            method_fn = getattr(sensors, self.sensorName)
            result = method_fn(self.post_value)
            header = {
                "method": "POST",
                "device": self.deviceName,
                "sensor": self.sensorName,
                "value": result,
            }
            payload = {"value": result}
            response = json.dumps({"header": header, "payload": payload})
            self.pub_client.publish(self.topic, response)
            self.pub_client.loop(timeout=1.0)
        except Exception:
            print(traceback.format_exc())
            error = json.dumps({
                "code": "ERROR",
                "number": 1,
                "message": f"There is no {self.sensorName} sensor in device {self.deviceName}",
            })
            self.pub_client.publish(self.topicError, error)
            self.pub_client.loop(timeout=1.0)


def on_disconnect(mqttc, obj, msg):
    print("disconnected tatu!")


def main(data, msg, stop_event):
    mqttBroker = data["mqttBroker"]
    mqttPort = data["mqttPort"]
    mqttUsername = data["mqttUsername"]
    mqttPassword = data["mqttPassword"]
    deviceName = data["deviceName"]
    topic = data["topicPrefix"] + deviceName + data["topicRes"]
    topicError = data["topicPrefix"] + deviceName + data["topicErr"]
    sensorsList = list(data["sensors"])

    try:
        msgJson = json.loads(msg.payload)
    except Exception:
        print(f"Invalid JSON payload: {msg.payload!r}")
        return

    sensorName = msgJson.get("sensor", deviceName)
    met = msgJson.get("method", "")

    if not met:
        print("Message missing 'method' field, ignoring.")
        return

    found = False
    if sensorName != deviceName:
        for sen in sensorsList:
            if sen["name"] == sensorName:
                sensorsList = [sen]
                found = True
                break
        if not found:
            sensorsList = []

    print("-------------------------------------------------")
    print("| Topic: " + str(msg.topic))
    print("| Message: " + str(msg.payload))
    print("-------------------------------------------------")

    idP = met + "_" + deviceName + "_" + sensorName

    pub_client = pub.Client(pub.CallbackAPIVersion.VERSION1, client_id="", clean_session=True, protocol=pub.MQTTv31)
    pub_client.on_disconnect = on_disconnect
    pub_client.username_pw_set(mqttUsername, mqttPassword)
    pub_client.connect(mqttBroker, mqttPort, 60)
    pub_client.loop(timeout=1.0)  # aguarda CONNACK antes de publicar

    if met == "POST":
        post_value = msgJson.get("value")
        sensor = virtualSensor(idP, deviceName, sensorName, sensorsList, met,
                                topic, topicError, pub_client, 0, 0, stop_event,
                                post_value=post_value)
    elif met == "GET":
        sensor = virtualSensor(idP, deviceName, sensorName, sensorsList, met,
                                topic, topicError, pub_client, 0, 0, stop_event)
    elif met == "FLOW":
        time_cfg = msgJson.get("time", {})
        collect = time_cfg.get("collect", 1)
        publish = time_cfg.get("publish", collect)
        sensor = virtualSensor(idP, deviceName, sensorName, sensorsList, met,
                                topic, topicError, pub_client, collect, publish, stop_event)
    elif met == "EVENT":
        time_cfg = msgJson.get("time", {})
        collect = time_cfg.get("collect", 1)
        sensor = virtualSensor(idP, deviceName, sensorName, sensorsList, met,
                                topic, topicError, pub_client, collect, 0, stop_event)
    else:
        print(f"Unknown method: {met}")
        return

    sensor.run()
