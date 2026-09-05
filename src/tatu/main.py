import paho.mqtt.client as mqtt
import json
import threading

from time import sleep

# You don't need to change this file. Just change sensors.py and config.json

_threads = []
_threads_lock = threading.Lock()


def _make_thread_id(method, device, sensor):
    return f"{method}_{device}_{sensor}"


def on_connect(mqttc, obj, flags, rc):
    topic = obj["topicPrefix"] + obj["deviceName"] + obj["topicReq"] + "/#"
    mqttc.subscribe(topic)
    print("Device's sensors:")
    for sensor in obj["sensors"]:
        print("\t" + sensor["name"])
    print("Topic device subscribed: " + topic)


def on_message(mqttc, obj, msg):
    if obj["topicReq"] in msg.topic:
        try:
            tatu_msg = json.loads(msg.payload)
        except Exception:
            print("Invalid JSON payload, ignoring message.")
            return
        if tatu_msg["method"] == "STOP":
            stop_sensor(obj, tatu_msg)
        else:
            init_sensor(obj, tatu_msg, msg)


def on_disconnect(mqttc, obj, rc):
    if rc == 0:
        print("Disconnected cleanly.")
    else:
        print(f"Unexpected disconnect (rc={rc}), reconnecting...")


def init_sensor(obj, tatu_msg, msg):
    import tatu
    thread_id = _make_thread_id(tatu_msg["method"], obj["deviceName"], tatu_msg["sensor"])
    t = threading.Thread(target=tatu.main, args=(obj, msg), name=thread_id, daemon=True)
    with _threads_lock:
        _threads.append(t)
    t.start()
    _cleanup_threads()


def stop_sensor(obj, tatu_msg):
    thread_id = _make_thread_id(tatu_msg["target"], obj["deviceName"], tatu_msg["sensor"])
    with _threads_lock:
        for t in list(_threads):
            if t.name == thread_id:
                print("Stopping thread " + t.name)
                _threads.remove(t)
                # Threads cannot be forcibly stopped; daemon=True ensures they
                # are cleaned up when the process exits. A future refactor can
                # add a stop Event per thread.
                break


def _cleanup_threads():
    with _threads_lock:
        done = [t for t in _threads if not t.is_alive()]
        for t in done:
            _threads.remove(t)


while True:
    with open("config.json") as f:
        data = json.load(f)

    mqttBroker = data["mqttBroker"]
    mqttPort = data["mqttPort"]
    mqttUsername = data["mqttUsername"]
    mqttPassword = data["mqttPassword"]
    deviceName = data["deviceName"]

    # For paho-mqtt 2.0+ use CallbackAPIVersion.VERSION1:
    sub_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, deviceName + "_sub", protocol=mqtt.MQTTv31)
    # For paho-mqtt 1.x use:
    # sub_client = mqtt.Client(deviceName + "_sub", protocol=mqtt.MQTTv31)

    sub_client.username_pw_set(mqttUsername, mqttPassword)
    sub_client.user_data_set(data)
    sub_client.on_connect = on_connect
    sub_client.on_message = on_message
    sub_client.on_disconnect = on_disconnect

    try:
        sub_client.connect(mqttBroker, mqttPort, 60)
        sub_client.loop_forever()
    except Exception:
        print("Broker unreachable on " + mqttBroker + " URL!")
        sleep(5)
