from flask import Flask, request, jsonify, send_from_directory, render_template
import json
import os
app = Flask(__name__, static_url_path='')

@app.route('/', methods=['GET', 'POST'])
def config():
	if request.method == 'GET':
		root_dir = os.path.dirname(os.getcwd())
		with open('config.json') as f:
  			data = json.load(f)
		return render_template("index.html", data=data)
	else:
		with open('config.json') as f:
			data = json.load(f)
		
		form_data = request.form
		
		data["mqttBroker"] = form_data["mqttBroker"]
		data["mqttPort"] = int(form_data["mqttPort"])
		data["mqttUsername"] = form_data["mqttUsername"]
		data["mqttPassword"] = form_data["mqttPassword"]

		data["deviceName"] = form_data["deviceName"]

		with open('config.json', 'w') as output:
			json.dump(data, output, indent=4)

		return jsonify(data)
