import paho.mqtt.client as mqtt
import json
import threading

from time import sleep

# You don't need to change this file. Just change sensors.py and config.json

_threads = {}  # thread_id -> (thread, stop_event)
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
    if obj["topicReq"] not in msg.topic:
        return
    try:
        tatu_msg = json.loads(msg.payload)
    except Exception:
        print("Invalid JSON payload, ignoring message.")
        return
    method = tatu_msg.get("method", "")
    if method == "STOP":
        stop_sensor(mqttc, obj, tatu_msg)
    elif method in ("GET", "FLOW", "EVENT", "POST"):
        init_sensor(obj, tatu_msg, msg)
    else:
        topicError = obj["topicPrefix"] + obj["deviceName"] + obj["topicErr"]
        mqttc.publish(topicError, json.dumps({"code": "UNKNOWN_METHOD", "message": method}))


def on_disconnect(mqttc, obj, rc):
    if rc == 0:
        print("Disconnected cleanly.")
    else:
        print(f"Unexpected disconnect (rc={rc}), reconnecting...")


def init_sensor(obj, tatu_msg, msg):
    import tatu
    sensor_name = tatu_msg.get("sensor", obj["deviceName"])
    thread_id = _make_thread_id(tatu_msg["method"], obj["deviceName"], sensor_name)
    stop_event = threading.Event()
    t = threading.Thread(target=tatu.main, args=(obj, msg, stop_event), name=thread_id, daemon=True)
    with _threads_lock:
        existing = _threads.pop(thread_id, None)
        if existing:
            _, old_stop = existing
            old_stop.set()
        _threads[thread_id] = (t, stop_event)
    t.start()
    _cleanup_threads()


def stop_sensor(mqttc, obj, tatu_msg):
    topicError = obj["topicPrefix"] + obj["deviceName"] + obj["topicErr"]
    target_method = tatu_msg.get("target", "FLOW")
    sensor_name = tatu_msg.get("sensor", "")
    if not sensor_name:
        mqttc.publish(topicError, json.dumps({"code": "INVALID_PARAMS", "message": "STOP requires sensor field"}))
        return
    thread_id = _make_thread_id(target_method, obj["deviceName"], sensor_name)
    with _threads_lock:
        entry = _threads.pop(thread_id, None)
    if entry:
        t, stop_event = entry
        stop_event.set()
        print(f"Stopping thread {thread_id}")
    else:
        mqttc.publish(topicError, json.dumps({"code": "STOP_NOT_FOUND", "message": f"{target_method} not found for sensor: {sensor_name}"}))
        print(f"No running thread found for {thread_id}")
    _cleanup_threads()


def _cleanup_threads():
    with _threads_lock:
        done = [tid for tid, (t, _) in _threads.items() if not t.is_alive()]
        for tid in done:
            del _threads[tid]


while True:
    with open("config.json") as f:
        data = json.load(f)

    mqttBroker = data["mqttBroker"]
    mqttPort = data["mqttPort"]
    mqttUsername = data["mqttUsername"]
    mqttPassword = data["mqttPassword"]
    deviceName = data["deviceName"]

    sub_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, deviceName + "_sub", protocol=mqtt.MQTTv31)
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
