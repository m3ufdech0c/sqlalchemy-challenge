# Import Flask and other required dependencies 
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt
import datedelta as dd

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:////Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

# Create my climate app
app = Flask(__name__)

#################################################
# Available Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the climate app!<br/>"
        f"Here is a list of the available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the precipitation analysis data as json"""

    # Calculate the date one year from the last date in data set.
    query_date_limit = dt.date(2017, 8, 23) - 12 * dd.MONTH

    # Perform a query to retrieve the data and precipitation scores
    one_yr_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date <= '2017-08-23').\
    filter(Measurement.date >= query_date_limit).order_by(Measurement.date.desc()).all()

    # Closing Session
    session.close()

    # Convert list of tuples into normal list
    prcp_by_date = list(np.ravel(one_yr_data))

    return jsonify(prcp_by_date)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a json list of stations from the dataset"""
    # Performing a query to list the stations names and codes
    stations = session.query(Station.name, Station.station).all()

    # Closing Session
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a json list of temperature observations for the previous year""" 
    
    # Calculate the date one year from the last date in data set.
    query_date_limit = dt.date(2017, 8, 23) - 12 * dd.MONTH

    # Performing a query to list the dates and temperature observations of the most-active station for the previous year of data
    last_yr_act_station = session.query(Measurement.station, func.count(Measurement.id)).\
    group_by(Measurement.station).\
        filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= query_date_limit).\
            order_by(func.count(Measurement.id).desc()).first()
    
    # Using the most active station from last yr resulted from the query above to print its tobs for last year
    last_yr_act_station_tobs = session.query(Measurement.tobs).\
    filter(Measurement.station == last_yr_act_station[0]).\
        filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= query_date_limit).all()

    # Closing Session
    session.close()

    # Convert list of tuples into normal list
    last_yr_act_station_tobs_list = list(np.ravel(last_yr_act_station_tobs))

    return jsonify(last_yr_act_station_tobs_list)

@app.route("/api/v1.0/<start>")
def measurement_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a json list of the minimum temperature, the average temperature, and the maximum temperature for a specified start"""
    
    # Performing a query for the min, avg and max tobs for date in the Measurement class equal or greater than the specified start date
    # In the process, we'll be creating labels for the diff tobs (min, avg and max) to be used to convert the resulting tuple into a dictionary
    sel = [func.min(Measurement.tobs).label("tmin"),
           func.avg(Measurement.tobs).label("tavg"),
           func.max(Measurement.tobs).label("tmax")]
    
    tobs_up_to_start_date = session.query(Measurement.date, *sel).group_by(Measurement.date).filter(Measurement.date >= start).all()
    
    # Converting the tuple from the above into a dictionary for dates greater or equal to start date
    tobs_up_to_start_date_dict = dict()
    for Measurement.date in tobs_up_to_start_date:
        tobs_up_to_start_date_dict.setdefault(Measurement.date, []).append(tmin)
        tobs_up_to_start_date_dict.setdefault(Measurement.date, []).append(tavg)
        tobs_up_to_start_date_dict.setdefault(Measurement.date, []).append(tmax)
         
    return tobs_up_to_start_date_dict
        


if __name__ == "__main__":
    app.run(debug=True)


