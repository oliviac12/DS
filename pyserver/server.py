#!flask/bin/python
from flask import Flask, jsonify
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from flask import request
from flask import Flask, render_template 
from flask import Flask, render_template, request
from flask import Flask, render_template, json, request
import requests

app = Flask(__name__)

uber_base_url = "https://api.uber.com/v1/estimates/price?"
google_base_url = "https://maps.googleapis.com/maps/api/directions/json?"
#https://maps.googleapis.com/maps/api/directions/json?origin=37.625732+-122.377807&destination=37.785114+-122.406677&key=AIzaSyD6DiPM0cuIqaEfa6Bk-fmp8oRW6UG2uUY
#https://api.uber.com/v1/estimates/price?start_latitude=37.625732&start_longitude=-122.377807&end_latitude=37.785114&end_longitude=-122.406677&server_token=27-zMQ7EpycOjn_qFBMWuI6Vb0QYJ6gcpPbaL5bE


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/uber_get_estimates/<string:query>', methods = ['GET'])
def uber_get_estimates(query):
    
    search_url = uber_base_url + query
    search_req = requests.get(search_url)
    search_json = search_req.json()

    return jsonify(search_json)


@app.route('/google_get_estimates/<string:query>', methods = ['GET'])
def google_get_estimates(query):

    search_url = google_base_url + query 
    #search_url = "https://maps.googleapis.com/maps/api/directions/json?origin=37.625732+-122.377807&destination=37.785114+-122.406677&key=AIzaSyD6DiPM0cuIqaEfa6Bk-fmp8oRW6UG2uUY"
    search_req = requests.get(search_url)
    search_json = search_req.json()

    return jsonify(search_json)


if __name__ == '__main__':
    app.run(debug=True)