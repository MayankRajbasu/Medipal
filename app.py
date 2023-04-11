from flask import Flask, render_template,request,redirect,url_for,session
from pymongo import MongoClient

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
    db.Doctors.insert_one({"Name": Name,"Phone":Phone,"Email": Email,"Department":Speciality,"License":License,"Practice":Years}) 
    # print(Name,Phone,Email,Speciality,License,Years)
    return redirect(url_for("login"))

@app.route("/log_submit", methods=['POST'])
def log_submit():
    LogDetails = request.form
    Name = LogDetails['name']
    License = LogDetails['licence']
    user = db.Doctors.find_one({"Name": Name,"License": License})
    if user:
        session['name'] = Name
        return redirect(url_for("home"))
    else:
        return redirect((url_for("login")))
    # return redirect(url_for("home"))

@app.route("/Consult")
def consult_doc():
    return render_template("consult.html")

@app.route("/Predict")
def predict():
    return render_template("predict.html")

if __name__ == '__main__':
	app.run(debug=True)
