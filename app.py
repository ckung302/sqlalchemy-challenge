
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, query
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd
import numpy as np
from flask import Flask, jsonify



engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

latest_date = session.query(measurement.date).order_by(measurement.date)[-1][0]
query_date = (dt.date(2017, 8, 23) - dt.timedelta(days=365))
query_date = query_date.strftime("%Y-%m-%d")

app = Flask(__name__)

welcome = ["Fuck this Homework I hate this"]

@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt, for example /api/v1.0/2015-01-01<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt, for example /api/v1.0/2015-01-01/2017-01-01"
    )

@app.route("/test")
def test():
    return jsonify(welcome)

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(measurement.date, func.avg(measurement.prcp)).filter(measurement.date >= query_date).group_by(measurement.date).all()
    
    output = []
    for date, prcp in results:
        output.append({str(date): prcp})
    return jsonify(output)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    output = list(np.ravel(results))
    return jsonify(output)    

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(measurement.date, func.avg(measurement.tobs)).filter(measurement.date >= query_date).group_by(measurement.date).all()
    output = []
    for date, temp in results:
        output.append({str(date): temp})
    return jsonify(output)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=latest_date):

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    if end == latest_date:
        end_date = end
    else:
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    temperatures = session.query(*sel).filter(measurement.date >= start_date).filter(measurement <= end_date).all()[0]

    output = [{'temp_min': temperatures[0]},
            {'temp_max': temperatures[1]},
            {'temp_avg': temperatures[2]}]
    
    return jsonify(output)

session.close()

if __name__ == "__main__":
    app.run(debug=True)