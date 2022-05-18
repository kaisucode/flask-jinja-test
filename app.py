from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
import os
import uuid
import requests
import io
import csv

PORT = 80
app = Flask(__name__)

# handle CORS
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

# mongodb setup
app.config["MONGO_URI"] = str(os.environ.get("MONGODB_PROD_STRING"))
mongo = PyMongo(app)
db = mongo.db

# weather api setup
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}"
API_KEY = str(os.environ.get("OPENWEATHER_API_KEY"))

cities = {
        "Boston": [42.21, 71.5], 
        "San Jose": [37.20, 121.53], 
        "Providence": [41.50, 71.24], 
        "Detroit": [42.20, 83.3], 
        "New York": [40.47, 73.58]
        }

test_data = [
        {
            "id": "1",
            "item_name": "Chocolate",
            "quantity": "500",
            "city": "Boston",
            "weather": "niceeeee"
            }, 

        {
            "id": "2",
            "item_name": "Coffee",
            "quantity": "300",
            "city": "San Jose",
            "weather": "extra niceee"
            }
        ]

@app.route('/index')
@app.route('/')
def index(): 
    entry_data = list(db.entries.find())
    return render_template('index.html', entries=entry_data)
    #  return render_template('index.html', entries=test_data)

@app.route('/download')
def download(): 
    entry_data = list(db.entries.find())

    si = io.StringIO()
    csv_data = csv.writer(si)

    for entry in entry_data: 
        row_data = []
        for key in entry: 
            row_data.append(entry[key])
        csv_data.writerow(row_data)
    ret = make_response(si.getvalue())
    ret.headers["Content-Disposition"] = "attachment; filename=inventory.csv"
    ret.headers["Content-type"] = "text/csv"
    return ret

@app.route('/form')
def form(): 
    return render_template('form.html', 
            title="Create",
            submitEndpoint="/createEntry",
            defaultItemName="Item",
            defaultCity="Boston,MA,USA",
            defaultQuantity=3,
            )

@app.route('/updateForm')
def updateForm(): 
    _id = request.args.get('hidden_id')
    item_name = request.args.get('hidden_item_name')
    city = request.args.get('hidden_city')
    weather = request.args.get('hidden_weather')
    quantity = request.args.get('hidden_quantity')

    print(request.args)

    return render_template('form.html', 
            title="Update",
            submitEndpoint="/editEntry",
            itemID=_id,
            weather=weather,

            defaultItemName=item_name,
            defaultCity=city,
            defaultQuantity=quantity,
            )

def getWeatherDescription(city): 
    res = requests.get(WEATHER_API_URL.format(city=city, apikey=API_KEY))
    if not res.ok: 
        print("failed to get weather information")
        return "Failed to get weather information", 500

    weather_data = res.json()["main"]
    description = res.json()["weather"][0]["description"]

    weather_description_template = "{desc}, temperature of {temp}, pressure of {pressure}, humidity of {humidity}"
    weather_description = weather_description_template.format(
            desc=description,
            temp=weather_data["temp"], 
            pressure=weather_data["pressure"], 
            humidity=weather_data["humidity"])

    return weather_description

@app.route('/createEntry', methods=["GET"])
def createEntry(): 

    args = request.args
    _id = str(uuid.uuid4())
    item_name = args.get('item_name')
    quantity = args.get('quantity')
    city = args.get('city')
    weather_description = getWeatherDescription(city)

    db.entries.insert_one({'id': _id, 'item_name': item_name, 'quantity': quantity, 
        'city': city, 'weather': weather_description})

    return redirect(url_for('index'), code=302)

@app.route('/editEntry', methods=["GET"])
def editEntry():
    args = request.args
    _id = args.get('id')
    item_name = args.get('item_name')
    quantity = args.get('quantity')
    city = args.get('city')
    weather_description = getWeatherDescription(city)

    updatedData = {'item_name': item_name, 'quantity': quantity, 
        'city': city, 'weather': weather_description}
    db.entries.update_one({'id': _id}, {"$set": updatedData})
    return redirect("/", code=302)

@app.route('/removeEntry', methods=["GET"])
def removeEntry():
    _id = request.args.get('hidden_id')
    db.entries.delete_one({'id': _id})
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

