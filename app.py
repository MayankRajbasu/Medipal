from flask import Flask, render_template,request,redirect,url_for,session
from pymongo import MongoClient
import pandas as pd
import numpy as np
import pickle

diab_model = pickle.load(open('diab_model.pkl', 'rb'))

app = Flask(__name__)
app.secret_key = 'super secret key'

# connect to MongoDB Atlas
client = MongoClient("mongodb://localhost:27017")
db = client.MediPal

# define routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/reg")
def register():
    return render_template("register.html")    

@app.route("/login")
def login():
    return render_template("login.html") 

@app.route("/reg_submit", methods=['POST'])
def reg_sumbit():
    DoctorDetails = request.form
    Name = DoctorDetails['name']
    Phone = DoctorDetails['phone']
    Email = DoctorDetails['email']
    Speciality = DoctorDetails['speciality']
    License = DoctorDetails['licence']
    Years = DoctorDetails['years']
    user = db.Doctors.find_one({"License": License})
    if user:
        return render_template("register.html", error="Doctor already registered")
    if not Name or not Phone or not Email or not Speciality or not License or not Years:
        return render_template("register.html", error="Please fill out all feild")
    db.Doctors.insert_one({"Name": Name,"Phone":Phone,"Email": Email,"Department":Speciality,"License":License,"Practice":Years}) 
    # print(Name,Phone,Email,Speciality,License,Years)
    return redirect(url_for("login"))

@app.route("/log_submit", methods=['POST'])
def log_submit():
    LogDetails = request.form
    Name = LogDetails['name']
    License = LogDetails['licence']
    user = db.Doctors.find_one({"Name": Name,"License": License})
    if not Name or not License :
        return render_template("login.html", error="Please fill out all feild")
    if user:
        session['name'] = Name
        return redirect(url_for("home"))
    else:
        return redirect((url_for("login")))
    # return redirect(url_for("home"))

@app.route("/feed_submit",methods=['POST'])
def feed_submit():
    Feedback = request.form
    email = Feedback['email']
    comment = Feedback['comment']
    if not email or not comment:
        return render_template("index.html", error="Please fill out all feild")
    db.Feedbacks.insert_one({"Email":email,"Comments":comment})
    return render_template("index.html", result="Thank you for your Feedback!")

@app.route("/Consult")
def consult_doc():
    return render_template("consult.html")

@app.route("/Predict")
def predict():
    return render_template("predict.html")

@app.route("/Predict/heart")
def pred_heart():
    return render_template("heart.html")

@app.route("/Predict/cancer")
def pred_cancer():
    return render_template("cancer.html")

@app.route("/Predict/liver")
def pred_liver():
    return render_template("liver.html")

@app.route("/Predict/diabetes")
def pred_diabetes():
    return render_template("diabetes.html")

# <!-- Pregnancies,Glucose,BloodPressure,Insulin,BMI,DiabetesPedigreeFunction,Age -->
@app.route("/Predict/diabetes/result",methods=['POST'])
def result_diabetes():
    result = request.form
    Name=result['name']
    Email=result['email']
    Phone=result['phone']
    Pregnancies= result['Pregnancies']
    Glucose= result['Glucose']
    BloodPressure=result['BloodPressure']
    Insulin=result['Insulin']
    BMI= result['BMI']
    # DiabetesPedigreeFunction=result['DiabetesPedigreeFunction']
    Age=result['Age']
    db.Patients.insert_one({"Name":Name,"Email":Email,"Phone":Phone})
    df=np.array([[Pregnancies,Glucose,BloodPressure,Insulin,BMI,Age]]).astype('float64')
    output=diab_model.predict(df)
    print(Name,Email,Phone,Pregnancies,Glucose,BloodPressure,Insulin,BMI,Age, output)
    return redirect(url_for('pred_diabetes'))

if __name__ == '__main__':
	app.run(debug=True)
