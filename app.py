# Import Dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Set up database
engine = create_engine("sqlite:///hawaii.sqlite?check_same_thread=False")

# reflect database into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create variables for each class
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link
session = Session(engine)

# Create a new Flask instance
app = Flask(__name__) # name variable denotes the name of the current function ("magic method")

# Begin creating routes
# Welcome Route
@app.route('/') # root
def welcome():
    return(
        '''
        Welcome to the Climate Analysis API!<br>
        Available Routes:<br>
        /api/v1.0/precipitation<br>
        /api/v1.0/stations<br>
        /api/v1.0/tobs<br>
        /api/v1.0/temp/start/end
        ''')

# Precipitation Route
# Note: Check Jupyter notebook for query building notes - these are just repeats of the SQLite queries
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    # this line creates a dictionary with the date as the key and precipitation as the value
    precip = {date: prcp for date, prcp in precipitation}
    # jsonify method converts dictionary to json file for easy viewing in the web app
    return jsonify(precip)

# Build Stations Route
@app.route("/api/v1.0/stations")
def stations():
    # Query for the stations, store in results, convert to a list with the name stations
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    # Return jsonify of the list
    return jsonify(stations=stations)

# Build tobs route
@app.route("/api/v1.0/tobs")
def temp_monthly():
# Calculate the date one year ago from the last date in the database (Jupyter)
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        # query the primary station for all the temperature observations from the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # Unravel into a list and jsonify
    temps = list(np.ravel(results)) 
    return jsonify(temps=temps)

# Build stats route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# Use parameters in the definition
def stats(start=None, end=None):
    # query for min, avg, max temp from sqlite
    # start with list
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # use an if not statement to loop through the list
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
            # unravel and jsonify
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

# repeat the code for some reason??
    results = session.query(*sel).\
         filter(Measurement.date >= start).\
         filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
