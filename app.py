from flask import Flask, request, render_template,make_response, redirect, url_for
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt
)
import json

import requests
from requests.auth import HTTPBasicAuth

from datetime import timedelta, datetime

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'secret'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)

events_number = 1
event_path="./events.json"

measurment_number = 1
iotdev_number = 1
iotdev_path="./IoTdev.json"
measurments_path="./measurments.json"

energy_path = "./energy.json"


admins = [{"username":"Acho", "password":"secret"}, {"username":"Awo", "password":"secret"}, {"username":"Henry", "password":"secret"}, {"username":"Dacho", "password":"secret"}]
users = [{"username":"Neighbours", "password":"password"}]

def get_values(path):
    try:
        with open(path, 'r') as file:
            data = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    return data

@jwt.unauthorized_loader
def unauthorized_response(callback):
    return render_template('No_access.html'), 403

@app.route('/')
def index():
    return render_template("Home.html")
@app.route('/monitoring')
@jwt_required()
def monitoring_page():
    jwt_tok = get_jwt()
    if jwt_tok.get('role') == "admin":
        return render_template("Monitoring.html", iotdev=get_values(iotdev_path), measurments=get_values(measurments_path))
    else:
        return render_template('No_access.html')
@app.route('/events')
@jwt_required()
def events_page():
    jwt_tok = get_jwt()
    return render_template("Events.html", events=get_values(event_path), role=jwt_tok.get('role'))
@app.route('/room')
def room_page():
    return render_template("Room.html")
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("Login.html")

@app.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect(url_for('index')))
    response.delete_cookie('access_token_cookie')
    return response

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("email")
    password = request.form.get('password')

    response = make_response(redirect(url_for('index')))

    for admin in admins:
        if admin['username'] == username:
            if admin['password'] == password:
                access_token = create_access_token(identity=username, additional_claims={"role": "admin"},expires_delta=timedelta(minutes=30))
                
                response = make_response(redirect(url_for('index')))
                response.set_cookie(
                    'access_token_cookie', 
                    access_token,
                    httponly=True,
                    samesite='Strict'
                )
    
    for user in users:
        if user['username'] == username:
            if user['password'] == password:
                access_token = create_access_token(identity=username, additional_claims={"role": "user"},expires_delta=timedelta(minutes=30))
                
                response = make_response(redirect(url_for('index')))
                response.set_cookie(
                    'access_token_cookie', 
                    access_token,
                    httponly=True,
                    samesite='Strict'
                )

    return response



def add_to_values(new_data, path):
    data = get_values(path)

    data.append(new_data)

    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/addEvent', methods=["GET"])
@jwt_required()
def add_event_page():
    return render_template("AddEvent.html")

@app.route('/addEvent', methods=["POST"])
@jwt_required()
def add_event():
    global events_number
    date = request.form.get("Date")
    time = request.form.get('Time')
    type_of_event = request.form.get("Type")
    what_to_get = request.form.get('What to bring')
    events_number += 1

    add_to_values({"id":events_number, "Date":date, "Time":time, "Type":type_of_event, "What to bring":what_to_get}, event_path)

    response = make_response(redirect(url_for('events_page')))

    return response

def delete_from_values(id, path):
    data = get_values(path)

    for i in range(len(data)):
        if data[i]["id"]==id:
            data.pop(i)
            break

    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/energyConsumption', methods=["GET"])
@jwt_required()
def energy_consumption_page():
    #global energy_path
    with open(energy_path, 'r') as file:
        data = json.load(file)

        date_today = str(datetime.now().month) + "-" + str(datetime.now().year)

        for i in range(len(data)):
            if data[i].get(date_today) != None:
                return render_template("EnergyConsumption.html", totalConsumption=data[i][date_today]["totalLoad"], price=round(data[i][date_today]["cost"], 2))
        
        return render_template("EnergyConsumption.html", totalConsumption="0", price="0")

@app.route('/deleteEvent', methods=["GET"])
@jwt_required()
def delete_event_page():
    return render_template("DeleteEvent.html")

@app.route('/deleteEvent', methods=["POST"])
@jwt_required()
def delete_event():
    global events_number
    id = int(request.form.get("ID"))

    delete_from_values(id, event_path)

    response = make_response(redirect(url_for('events_page')))

    return response

@app.route('/addIoTdevice', methods=["GET"])
@jwt_required()
def add_IoTdev_page():
    return render_template("AddIoTdevice.html")

@app.route('/addIoTdevice', methods=["POST"])
def add_iot_dev():
    global iotdev_number
    name = request.form.get("Name")
    job = request.form.get('Job')
    desc = request.form.get('Description')

    iotdev_number += 1

    add_to_values({"id":iotdev_number, "Name":name, "Job":job, "Description":desc}, iotdev_path)

    response = make_response(redirect(url_for('monitoring_page')))

    return response

@app.route('/addMeasurment', methods=["POST"])
def add_measurment():
    global measurment_number
    data = request.get_json()
    name = data["Sensor name"]
    measure = data['Measure']
    value = data['Sensor Value']
    uom = data["Sensor Unit of measurment"]

    measurment_number += 1

    add_to_values({"id":measurment_number, "Sensor name":name, "Mesaure":measure, "Sensor value":value, "Sensor Unit of measurment":uom}, measurments_path)

    response = make_response(redirect(url_for('monitoring_page')))

    return response

@app.route('/deleteIoTdevice', methods=["GET"])
@jwt_required()
def delete_IoTdev_page():
    return render_template("DeleteIoTdevice.html")

@app.route('/deleteIoTdevice', methods=["POST"])
@jwt_required()
def delete_IoTdev():
    global events_number
    id = int(request.form.get("ID"))

    delete_from_values(id, iotdev_path)

    response = make_response(redirect(url_for('monitoring_page')))

    return response

@app.route('/deleteMeasurment', methods=["GET"])
@jwt_required()
def delete_measurment_page():
    return render_template("DeleteMeasurment.html")

@app.route('/deleteMeasurment', methods=["POST"])
@jwt_required()
def delete_measurment():
    global events_number
    id = int(request.form.get("ID"))

    delete_from_values(id, measurments_path)

    response = make_response(redirect(url_for('monitoring_page')))

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)