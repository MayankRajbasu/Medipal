from flask import Flask, render_template,request,redirect,url_for,session
from pymongo import MongoClient
import pandas as pd
import numpy as np
import pickle

diab_model = pickle.load(open('diab_model.pkl', 'rb'))
heart_model= pickle.load(open('heartmodel.pkl', 'rb'))
livermodel= pickle.load(open('livermodel.pkl', 'rb'))
b_cancermodel= pickle.load(open('b_cancermodel.pkl', 'rb'))

app = Flask(__name__)
app.secret_key = 'super secret key'

# connect to MongoDB Atlas
client = MongoClient("mongodb://localhost:27017")
# client = MongoClient("mongodb+srv://Moinak:mypassword@mayank.hkjmdfh.mongodb.net/?retryWrites=true&w=majority")
db = client.MediPal
collection = db['Blogs']

# define routes
@app.route("/")
def home():
    error = request.args.get('error')
    result = request.args.get('result')
    return render_template("index.html", error=error,result=result)

@app.route("/reg")
def register():
    error = request.args.get('error')
    return render_template("register.html",error=error)    

@app.route("/login")
def login():
    error = request.args.get('error')
    return render_template("login.html", error=error)

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
        return redirect(url_for('register', error="Please fill out all feild"))
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
        return redirect(url_for("login", error="Please fill out all feild"))
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
        return redirect(url_for("home", error="Please fill out all feild for your Feedback"))
    db.Feedbacks.insert_one({"Email":email,"Comments":comment})
    return redirect(url_for("home",result="Thank you for your Feedback!") )

@app.route("/Consult")
def consult_doc():
    return render_template("consult.html")

@app.route("/Predict")
def predict():
    return render_template("predict.html")

@app.route("/Predict/heart")
def pred_heart():
    error = request.args.get('error')
    return render_template("heart.html",error=error)

# <!-- Age,Sex,ChestPainType,RestingBP,Cholesterol,FastingBS,RestingECG,MaxHR,ExerciseAngina,Oldpeak,ST_Slope,Target-->
@app.route("/Predict/heart/result",methods=['POST'])
def result_heart():
    result=request.form
    Name=result['name']
    Email=result['email']
    Phone=result['phone']
    Age=result['Age']
    Sex=result['Sex']
    ChestPainType=result['ChestPainType']
    RestingBP=result['RestingBP']
    Cholesterol= result['Cholesterol']
    FastingBS= result['FastingBS']
    RestingECG= result['RestingECG']
    MaxHR= result['MaxHR']
    ExerciseAngina= result['ExerciseAngina']
    Oldpeak= result['Oldpeak']
    ST_Slope= result['ST_Slope']

    if not Name or not Email or not Phone or not Age or not Sex or not ChestPainType or not RestingBP or not Cholesterol or not FastingBS or not RestingECG or not MaxHR or not ExerciseAngina or not Oldpeak or not ST_Slope:
        return redirect(url_for('pred_heart', error="Please fill out all feild!!"))
    db.Patients.insert_one({"Name":Name,"Email":Email,"Phone":Phone})
    df=np.array([[Age,Sex,ChestPainType,RestingBP,Cholesterol,FastingBS,RestingECG,MaxHR,ExerciseAngina,Oldpeak,ST_Slope]]).astype('float64')
    output=heart_model.predict(df)
    print(Name,Email,Phone,Age,Sex,ChestPainType,RestingBP,Cholesterol,FastingBS,RestingECG,MaxHR,ExerciseAngina,Oldpeak,ST_Slope, output)
    return redirect(url_for('pred_heart'))

@app.route("/Predict/cancer")
def pred_cancer():
    error = request.args.get('error')
    return render_template("cancer.html",error=error)




@app.route("/Predict/liver")
def pred_liver():
    error = request.args.get('error')
    return render_template("liver.html",error=error)

@app.route("/Predict/diabetes")
def pred_diabetes():
    error = request.args.get('error')
    return render_template("diabetes.html",error=error)

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
    Age=result['Age']
    if not Name or not Email or not Phone or not Pregnancies or not Glucose or not BloodPressure or not Insulin or not BMI or not Age:
        return redirect(url_for('pred_diabetes', error="Please fill out all feild!!"))
    db.Patients.insert_one({"Name":Name,"Email":Email,"Phone":Phone})
    df=np.array([[Pregnancies,Glucose,BloodPressure,Insulin,BMI,Age]]).astype('float64')
    output=diab_model.predict(df)
    if output == [0]:
        return redirect(url_for('blog_diabetes', result="You don't have any possiblity for diabetes."))
    if output == [1]:
        return redirect(url_for('blog_diabetes', error="You have possiblity for diabetes."))
    print(Name,Email,Phone,Pregnancies,Glucose,BloodPressure,Insulin,BMI,Age, output)
    return redirect(url_for('pred_diabetes'))

@app.route("/Blogs/Diabetes")
def blog_diabetes():
    error = request.args.get('error')
    result = request.args.get('result')
    post = collection.find_one({'_id': '4'})
    return render_template('blogs.html', post=post,error=error,result=result)

if __name__ == '__main__':
	app.run(debug=True)
