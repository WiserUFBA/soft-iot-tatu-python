import paho.mqtt.client as pub
import sensors
import json
import time
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

    def _pub_err(self, code, message=''):
        payload = {'code': code}
        if message:
            payload['message'] = message
        self.pub_client.publish(self.topicError, json.dumps(payload))

    def _advance(self, deadline, period, now):
        diff = now - deadline
        return deadline + (int(diff / period) + 1) * period

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
        print("Stopping thread " + self.processID)

    def buildFlowAnswerDevice(self):
        try:
            sensor_dict = {x["name"]: [] for x in self.sensorsList}
            collect_deadline = time.monotonic() + self.collectTime
            publish_deadline = time.monotonic() + self.publishTime

            while True:
                now = time.monotonic()
                wait_s = max(0.0, min(collect_deadline, publish_deadline) - now)
                if self.stop_event.wait(timeout=wait_s):
                    break

                now = time.monotonic()

                if now >= collect_deadline:
                    for i in self.sensorsList:
                        sn = i["name"]
                        sensor_dict[sn].append(getattr(sensors, sn)())
                    collect_deadline = self._advance(collect_deadline, self.collectTime, now)

                if now >= publish_deadline:
                    header = {
                        "method": "FLOW",
                        "device": self.deviceName,
                        "sensor": self.sensorName,
                        "time": {"collect": self.collectTime, "publish": self.publishTime},
                    }
                    payload = {"sensors": [{n: list(v)} for n, v in sensor_dict.items()]}
                    self.pub_client.publish(self.topic, json.dumps({"header": header, "payload": payload}))
                    publish_deadline = self._advance(publish_deadline, self.publishTime, now)
                    for name in sensor_dict:
                        sensor_dict[name] = []

        except Exception:
            print(traceback.format_exc())
            self._pub_err("SENSOR_READ_ERROR", "Error reading sensor")

    def buildEventAnswerDevice(self):
        try:
            method_fn = getattr(sensors, self.sensorName)
            value = method_fn()
            header = {
                "method": "EVENT",
                "device": self.deviceName,
                "sensor": self.sensorName,
                "time": {"collect": self.collectTime, "publish": self.publishTime},
            }
            # publica valor inicial como referência
            self.pub_client.publish(self.topic, json.dumps({
                "header": header,
                "payload": {"sensors": [{self.sensorName: [value]}]},
            }))

            if self.publishTime == 0:
                # modo imediato: publica na mudança
                while not self.stop_event.wait(timeout=self.collectTime):
                    aux = method_fn()
                    if aux != value:
                        value = aux
                        self.pub_client.publish(self.topic, json.dumps({
                            "header": header,
                            "payload": {"sensors": [{self.sensorName: [value]}]},
                        }))
            else:
                # modo janela: bufferiza mudanças, publica em lote
                buf = []
                collect_deadline = time.monotonic() + self.collectTime
                publish_deadline = time.monotonic() + self.publishTime

                while True:
                    now = time.monotonic()
                    wait_s = max(0.0, min(collect_deadline, publish_deadline) - now)
                    if self.stop_event.wait(timeout=wait_s):
                        break

                    now = time.monotonic()

                    if now >= collect_deadline:
                        aux = method_fn()
                        if aux != value:
                            value = aux
                            if len(buf) < 30:
                                buf.append(value)
                        collect_deadline = self._advance(collect_deadline, self.collectTime, now)

                    if now >= publish_deadline:
                        if buf:
                            self.pub_client.publish(self.topic, json.dumps({
                                "header": header,
                                "payload": {"sensors": [{self.sensorName: list(buf)}]},
                            }))
                            buf = []
                        publish_deadline = self._advance(publish_deadline, self.publishTime, now)

        except Exception:
            print(traceback.format_exc())
            self._pub_err("SENSOR_READ_ERROR", f"Error reading {self.sensorName}")

    def buildGetAnswerDevice(self):
        try:
            sensor_dict = {x["name"]: [getattr(sensors, x["name"])()] for x in self.sensorsList}
            header = {"method": "GET", "device": self.deviceName, "sensor": self.sensorName}
            payload = {"sensors": [{n: v} for n, v in sensor_dict.items()]}
            self.pub_client.publish(self.topic, json.dumps({"header": header, "payload": payload}))
        except Exception:
            print(traceback.format_exc())
            self._pub_err("SENSOR_READ_ERROR", f"Error reading {self.sensorName}")

    def buildPostAnswerDevice(self):
        try:
            method_fn = getattr(sensors, self.sensorName)
            result = method_fn(self.post_value)
            header = {
                "method": "POST",
                "device": self.deviceName,
                "sensor": self.sensorName,
                "value": result,
            }
            self.pub_client.publish(self.topic, json.dumps({"header": header, "payload": {"value": result}}))
        except Exception:
            print(traceback.format_exc())
            self._pub_err("SENSOR_READ_ERROR", f"Error in POST for {self.sensorName}")


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

    if sensorName != deviceName:
        found = [s for s in sensorsList if s["name"] == sensorName]
        sensorsList = found

    print("-------------------------------------------------")
    print("| Topic: " + str(msg.topic))
    print("| Message: " + str(msg.payload))
    print("-------------------------------------------------")

    idP = met + "_" + deviceName + "_" + sensorName

    pub_client = pub.Client(pub.CallbackAPIVersion.VERSION1, client_id="", clean_session=True, protocol=pub.MQTTv31)
    pub_client.on_disconnect = on_disconnect
    pub_client.username_pw_set(mqttUsername, mqttPassword)
    pub_client.connect(mqttBroker, mqttPort, 60)
    pub_client.loop_start()

    def pub_err(code, message=''):
        payload = {'code': code}
        if message:
            payload['message'] = message
        pub_client.publish(topicError, json.dumps(payload))
        time.sleep(0.3)

    if not sensorsList:
        pub_err("SENSOR_NOT_FOUND", sensorName)
        pub_client.loop_stop()
        return

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
        try:
            collect = int(time_cfg.get("collect", 1))
            publish = int(time_cfg.get("publish", collect))
        except Exception:
            pub_err("INVALID_PARAMS", "Invalid time parameters")
            pub_client.loop_stop()
            return
        if collect <= 0 or publish < collect:
            pub_err("INVALID_PARAMS", f"collect={collect} publish={publish}")
            pub_client.loop_stop()
            return
        sensor = virtualSensor(idP, deviceName, sensorName, sensorsList, met,
                                topic, topicError, pub_client, collect, publish, stop_event)
    elif met == "EVENT":
        time_cfg = msgJson.get("time", {})
        try:
            collect = int(time_cfg.get("collect", 1))
            publish = int(time_cfg.get("publish", 0))
        except Exception:
            pub_err("INVALID_PARAMS", "Invalid time parameters")
            pub_client.loop_stop()
            return
        if collect <= 0:
            pub_err("INVALID_PARAMS", "collect must be > 0")
            pub_client.loop_stop()
            return
        if publish > 0 and publish < collect:
            pub_err("INVALID_PARAMS", "publish must be >= collect")
            pub_client.loop_stop()
            return
        sensor = virtualSensor(idP, deviceName, sensorName, sensorsList, met,
                                topic, topicError, pub_client, collect, publish, stop_event)
    else:
        pub_client.loop_stop()
        return

    sensor.run()
    pub_client.loop_stop()
    pub_client.disconnect()
