import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite").connect()

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
#session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Last 12 months"""
    # Query all passengers
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    latest_date = dt.datetime(int(most_recent[0][0:4]), int(most_recent[0][5:7]), int(most_recent[0][8:10]))

    # Calculate the date one year from the last date in data set.
    earliest_date = dt.datetime(int(most_recent[0][0:4])-1, int(most_recent[0][5:7]), int(most_recent[0][8:10]))

    # Perform a query to retrieve the data and precipitation scores
    last_12 = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date < latest_date).filter(Measurement.date > earliest_date).all()
    
    return_dict = {}
    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    for day in last_12:
        if day.date in return_dict:
            return_dict[day.date].append(day.prcp)
        else:
            return_dict[day.date] = [day.prcp]
    
    session.close()
    return jsonify(return_dict)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_list = session.query(Station.station).all()
    return jsonify([station[0] for station in stations_list])
    session.close()
    
    
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    latest_date = dt.datetime(int(most_recent[0][0:4]), int(most_recent[0][5:7]), int(most_recent[0][8:10]))
    
    earliest_date = dt.datetime(int(most_recent[0][0:4])-1, int(most_recent[0][5:7]), int(most_recent[0][8:10]))
    
    last_12_USC00519281 = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date < latest_date).filter(Measurement.date > earliest_date).all()
    
    session.close()

    return jsonify([x[1] for x in last_12_USC00519281])


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    
    start_date = dt.datetime(int(start[0:4]), int(start[5:7]), int(start[8:10]))

    summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    return jsonify([x for x in summary[0]])
    
    session.close()
    
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    session = Session(engine)

    start_date = dt.datetime(int(start[0:4]), int(start[5:7]), int(start[8:10]))
    end_date = dt.datetime(int(end[0:4]), int(end[5:7]), int(end[8:10]))

    summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end_date).all()
    
    return jsonify([x for x in summary[0]])

    session.close()

if __name__ == '__main__':
    app.run(debug=True)

