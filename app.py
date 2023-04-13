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

####################################### connect to MongoDB Atlas #######################################

client = MongoClient("mongodb://localhost:27017")
db = client.MediPal
collection = db['Blogs']

####################################### General Routes #######################################

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
    return redirect((url_for("login", error="Not Registred User. Register Yourself")))

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


####################################### Heart Diseases #######################################

@app.route("/Predict/heart")
def pred_heart():
    error = request.args.get('error')
    return render_template("heart.html",error=error)

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
    if output == [0]:
        return redirect(url_for('blog_heart', result="You don't have any possiblity for any Heart Diseases."))
    return redirect(url_for('blog_heart', error="You have very high possiblity for Heart Diseases."))
    

@app.route("/Blogs/Heart")
def blog_heart():
    error = request.args.get('error')
    result = request.args.get('result')
    post = collection.find_one({'_id': '1'})
    return render_template('blogs.html', post=post,error=error,result=result)

####################################### Breast Cancer #######################################

@app.route("/Predict/cancer")
def pred_cancer():
    error = request.args.get('error')
    return render_template("cancer.html",error=error)

@app.route("/Predict/cancer/result",methods=['POST'])
def result_Bcancer():
    result=request.form
    Name=result['name']
    Email=result['email']
    Phone=result['phone']
    clump_thickness=result['clump_thickness']
    uniform_cell_size=result['uniform_cell_size']
    uniform_cell_shape=result['uniform_cell_shape']
    marginal_adhesion=result['marginal_adhesion']
    single_epithelial_size=result['single_epithelial_size']
    bland_chromatin=result['bland_chromatin']
    normal_nucleoli=result['normal_nucleoli']
    mitoses=result['mitoses']
    if not Name or not Email or not Phone or not clump_thickness or not uniform_cell_size or not uniform_cell_shape or not marginal_adhesion or not single_epithelial_size or not bland_chromatin or not normal_nucleoli or not mitoses:
        return redirect(url_for('pred_cancer', error="Please fill out all feild!!"))
    db.Patients.insert_one({"Name":Name,"Email":Email,"Phone":Phone})
    df=np.array([[clump_thickness, uniform_cell_size, uniform_cell_shape, marginal_adhesion, single_epithelial_size, bland_chromatin, normal_nucleoli, mitoses]]).astype('float64')
    output=b_cancermodel.predict(df)
    if output == [2]:
        return redirect(url_for('blog_Bcancer', error="You Have low risk for Breast Cancer."))
    return redirect(url_for('blog_Bcancer', error="You have very high risk for Breast Cancer."))

@app.route("/Blogs/Breast Cancer")
def blog_Bcancer():
    error = request.args.get('error')
    result = request.args.get('result')
    post = collection.find_one({'_id': '2'})
    return render_template('blogs.html', post=post,error=error,result=result)

####################################### Liver Diseases #######################################

@app.route("/Predict/liver")
def pred_liver():
    error = request.args.get('error')
    return render_template("liver.html",error=error)

@app.route("/Predict/liver/result",methods=['POST'])
def result_liver():
    result=request.form
    Name=result['name']
    Email=result['email']
    Phone=result['phone']
    Age= result['Age']
    Gender= result['Gender']
    Total_Bilirubin= result['Total_Bilirubin']
    Direct_Bilirubin= result['Direct_Bilirubin']
    Alkaline_Phosphotase= result['Alkaline_Phosphotase']
    Alamine_Aminotransferase= result['Alamine_Aminotransferase']
    Aspartate_Aminotransferase= result['Aspartate_Aminotransferase']
    Total_Protiens= result['Total_Protiens']
    Albumin= result['Albumin']
    Albumin_and_Globulin_Ratio= result['Albumin_and_Globulin_Ratio']    

    if not Name or not Email or not Phone or not Age or not Gender or not Total_Bilirubin or not Direct_Bilirubin or not Alkaline_Phosphotase or not Alamine_Aminotransferase or not Aspartate_Aminotransferase or not Total_Protiens or not Albumin or not Albumin_and_Globulin_Ratio:
        return redirect(url_for('pred_liver', error="Please fill out all feild!!"))
    db.Patients.insert_one({"Name":Name,"Email":Email,"Phone":Phone})
    df=np.array([[Age,Gender,Total_Bilirubin,Direct_Bilirubin,Alkaline_Phosphotase,Alamine_Aminotransferase,Aspartate_Aminotransferase,Total_Protiens,Albumin,Albumin_and_Globulin_Ratio]]).astype('float64')
    output=livermodel.predict(df)
    if output == 2:
        return redirect(url_for('blog_liver', error="You Have low risk for Liver Diseases."))
    return redirect(url_for('blog_liver', error="You have very high risk for Liver Diseases."))

@app.route("/Blogs/liver")
def blog_liver():
    error = request.args.get('error')
    result = request.args.get('result')
    post = collection.find_one({'_id': '3'})
    return render_template('blogs.html', post=post,error=error,result=result)

####################################### Diabetes #######################################

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
    return redirect(url_for('blog_diabetes', error="You have very high possiblity for diabetes."))

@app.route("/Blogs/Diabetes")
def blog_diabetes():
    error = request.args.get('error')
    result = request.args.get('result')
    post = collection.find_one({'_id': '4'})
    return render_template('blogs.html', post=post,error=error,result=result)

####################################### Main Run #######################################

if __name__ == '__main__':
	app.run(debug=True)
