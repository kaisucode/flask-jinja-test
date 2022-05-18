from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
import os
import uuid
import requests


#  WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&dt=1643803200&appid={apikey}"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}"

PORT = 5000
app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

app.config["MONGO_URI"] = str(os.environ.get("AARI_MONGO_STRING"))
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

#  @app.route('/form', methods=["POST"])
#  def createEntry():
    #  return redirect("/", code=302)

    args = request.args
   
    if not args: 
        print("endpoint received")
        return render_template('form.html', entries=test_data)

    print("creating item")

    #  item_name = request.form.get('item_name')
    #  quantity = request.form.get('quantity')
    #  city = request.form.get('city')
    _id = uuid.uuid4()
    item_name = args.get('item_name')
    quantity = args.get('quantity')
    city = args.get('city')

    print(args)
    #  print(request.form)
    print("item_name: ", item_name)
    print("city: ", city)
    #  if (city not in cities): 
    #      return "Invalid city", 500

    #  lat = cities[city][0]
    #  lon = cities[city][1]

    print(WEATHER_API_URL.format(city=city, apikey=API_KEY))
    res = requests.get(WEATHER_API_URL.format(city=city, apikey=API_KEY))
    #  print(WEATHER_API_URL.format(lat=lat, lon=lon, apikey=API_KEY))
    #  res = requests.get(WEATHER_API_URL.format(lat=lat, lon=lon, apikey=API_KEY))
    if not res.ok: 
        print("failed to get weather information")
        print(res)
        return "Failed to get weather information", 500

    #  print("hello, res:")
    #  print(res)
    #  print(res.json())
    weather_data = res.json()["main"]
    description = res.json()["weather"][0]["description"]

    #  print(weather_data)
    weather_description_template = "{desc}, temperature of {temp}, pressure of {pressure}, humidity of {humidity}"
    weather_description = weather_description_template.format(
            desc=description,
            temp=weather_data["temp"], 
            pressure=weather_data["pressure"], 
            humidity=weather_data["humidity"])

    return redirect(url_for('index'), code=302)
    db.entries.insert_one({'id': _id, 'item_name': item_name, 'quantity': quantity, 
        'city': city, 'weather': weather_description})

    #  return "Entry created successfully!", 200
    return redirect("/", code=302)


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

