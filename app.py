from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
import os
import uuid
import requests


WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}"

PORT = 5000
app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

app.config["MONGO_URI"] = str(os.environ.get("MONGODB_PROD_STRING"))
API_KEY = str(os.environ.get("OPENWEATHER_API_KEY"))
mongo = PyMongo(app)
db = mongo.db

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
            "name": "Chocolate",
            "quantity": "500",
            "city": "Boston",
            "weather": "niceeeee"
            }, 

        {
            "id": "2",
            "name": "Coffee",
            "quantity": "300",
            "city": "San Jose",
            "weather": "extra niceee"
            }
        ]

@app.route('/index')
@app.route('/')
def index(): 
#      result = db.entries.find()
#      return flask.jsonify(result)
    return render_template('index.html', entries=test_data)

@app.route('/form')
def form(): 

    args = request.args
   
    if not args: 
        print("endpoint received")
        return render_template('form.html', entries=test_data)

    _id = str(uuid.uuid4())
    item_name = args.get('item_name')
    quantity = args.get('quantity')
    city = args.get('city')

    print(WEATHER_API_URL.format(city=city, apikey=API_KEY))
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

    db.entries.insert_one({'id': _id, 'item_name': item_name, 'quantity': quantity, 
        'city': city, 'weather': weather_description})

    return redirect(url_for('index'), code=302)
    #  return "Entry created successfully!", 200
    #  return redirect("/", code=302)


@app.route('/editItem', methods=["POST"])
def editEntry():
    _id = request.form.get('id')
    result = db.entries.update({'id': _id}, request.form.get("updates"))
    #  item_name = request.form.get('item_name')
    #  quantity = request.form.get('quantity')
    #  city = request.form.get('city')
    #  weather_description = request.form.get('weather_description')
    #  return "Entry edited successfully!", 200
    return redirect("/", code=302)

@app.route('/removeItem', methods=["POST"])
def removeEntry():
    _id = request.form.get('id')
    db.entries.delete_one({'id': _id})
    #  return "Entry removed successfully!", 200
    return redirect("/", code=302)

#  @app.route('/readAllItems', methods=["GET"])
#  def readEntry():
#      result = db.entries.find()
#      return flask.jsonify(result)

if __name__ == "__main__":
    app.run(host="localhost", port=PORT, debug=True)

