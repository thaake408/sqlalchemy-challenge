# Import dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Aloha! Welcome to the official Hawaii Climate API!<br/><br>"
        f"To navigate this API, please follow the Available Routes listed below:<br/><br>"
        f"-- Hawaii's Precipitation Totals from 2017: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"-- Hawaii's Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"-- Station USC00519281 Observations from 2017: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"-- Minimum, Average, & Maximum Temperatures by Date;<br/>To research this data, insert the start and end dates using 'yyyy-mm-dd' format in your browser's URL: <a href=\"/api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd\">/api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd<a><br>"
        f"Note: If no end-date is entered, the end date will default to 08/23/17<br>" 
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session
    session = Session(engine)

    # Query precipitation for all stations for the last year
    start_date = '2016-08-23'
    sel = [Measurement.date, 
        func.sum(Measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(Measurement.date >= start_date).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
   
    session.close()

    # Create dictionary with dates as keys and precipitation totals as values
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session 
    session = Session(engine)

    # Create list of stations in Hawaii
    sel = [Measurement.station]
    active_stations = session.query(*sel).\
        group_by(Measurement.station).all()
    session.close()

    # Create dictionary with dates as keys and precipitation totals as values
    # JSonify list
    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session 
    session = Session(engine)
    # Query last 12 months of temperature data for station USC00519281
    start_date = '2016-08-23'
    sel = [Measurement.date, 
        Measurement.tobs]
    station_temps = session.query(*sel).\
            filter(Measurement.date >= start_date, Measurement.station == 'USC00519281').\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()

    session.close()

    # Create dictionary with dates as keys and temperatures as values
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

@app.route("/api/v1.0/trip/<start_date>")
def trip1(start_date, end_date='2017-08-23'):
    # Calculate min, avg and max temps for range of dates
    # Format so if no end date is entered, it will select 2017-08-23 by default.

    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If query returns non-null values or no date is entered, display the following error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date {start_date} cannot be located or date is not entered in the following format: YYYY-MM-DD Please try again"}), 404
  
@app.route("/api/v1.0/trip/<start_date>/<end_date>")
def trip2(start_date, end_date='2017-08-23'):
    # Calculate min, avg and max temps for range of dates
    # Format so if no end date is entered, it will select 2017-08-23 by default.

    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If query returns non-null values or no date is entered, display the following error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date(s) cannot be located or date is not entered in the following format: YYYY-MM-DD Please try again"}), 404
  

if __name__ == '__main__':
    app.run(debug=True)