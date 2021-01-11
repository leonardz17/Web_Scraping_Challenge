# import libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# create instance of Flask app
app = Flask(__name__)

mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_info")

# create route that renders index.html template
@app.route("/")
def home():

    mars_data = mongo.db.mars_site.find_one()
    print(mars_data)
    return render_template("index.html",  mars = mars_data)

@app.route("/scrape")
def scrape():

    # Run the scrape function
    mars_all = scrape_mars.scrape_info()

    # Update the Mongo database using update and upsert=True
    mongo.db.mars_site.update({}, mars_all, upsert=True)

    # Redirect back to home page
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)