#import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#Setup database
#create engine
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################
# reflect database and tables created 
Base = automap_base()
Base.prepare(engine, reflect=True)
#################################################
# Reference for tables 
Measurement = Base.classes.measurement
Station = Base.classes.station 
#################################################
#opening the connection 
session = Session(engine)
#################################################
app = Flask(__name__)
#################################################
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()






#################################################
@app.route("/")
def home():
   
    """Lists all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
      
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Received precipitation api request.")

    #We find precipitation data for the last year.  First we find the last date in the database
    last_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = last_date[0][0]
    max_date = dt.datetime.strptime(max_date, "%Y-%m-%d")

    #set beginning of search query
    start_date = max_date - dt.timedelta(365)

    #find dates and precipitation amounts
    precipitation_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).all()
    
    
    #prepare the dictionary with the date as the key and the prcp value as the value
    results = {}
    for result in precipitation_data:
        results[result[0]] = result[1]

    return jsonify(results)
 


@app.route("/api/v1.0/stations")
def stations():
    print("Received station api request.")
     
    station_data = session.query(Station).all()

      #creating a list of dictionaries
    stations_list = []

    for station in station_data:
        station_dict = {}

        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)
        
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
     """Return a JSON list of temperature observations for the previous year."""

     print("Received tobs api request.")

     #We find temperature data for the last year.  First we find the last date in the database
     end_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
     max_date = end_date[0][0]
     max_date = dt.datetime.strptime(max_date, "%Y-%m-%d")

     #set beginning of search query
     start_date = max_date - dt.timedelta(365)

     #get temperature measurements for last year
     results = session.query(Measurement).\
         filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).all()

     #create list of dictionaries (one for each observation)
     tobs_list = []
     for result in results:
         tobs_dict = {}
         tobs_dict["date"] = result.date
         tobs_dict["tobs"] = result.tobs
         tobs_list.append(tobs_dict)

     return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date until
    the end of the database."""

    print("Received start date api request.")

    #First we find the last date in the database
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date_query[0][0]

    #get the temperatures
    temps = calc_temps(start, max_date)

    #create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date unitl
    the end date."""

    print("Received start date and end date api request.")

    #get the temperatures
    temps = calc_temps(start, end)

    #create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)





#code to actually run
if __name__ == "__main__":
    app.run(debug = True)

