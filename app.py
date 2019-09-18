from flask import Flask, request, url_for,render_template
from PIL import Image
import cv2

import sys
import os
import glob
import re
from pathlib import Path

from flask_pymongo import PyMongo

from fastai import *
from fastai.vision import *



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
mongo = PyMongo(app)

learn = load_learner('')

def model_predict(img_path):
    img = open_image(img_path)
    pred_class,pred_idx,outputs = learn.predict(img)
    return pred_class



@app.route('/')
def predict():
    img1 = "static/uploads/000001.jpg"
    preds = model_predict(img1)
    return render_template('index.html',pred=preds)

@app.route('/upload')
def imgupload():
    onl = mongo.db.imgatt1.find_one()
    return render_template('file.html', onl= onl)


@app.route('/home', methods=['GET','POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html')
    if request.method == 'POST':
        hc=request.form['HairColour']
        ht=request.form['HairType']
        b=request.form['Beard']
        ey=request.form['Eyebrows']
        na=request.form['Nose']
        nc=request.form['gender']
        if nc == "male":
            n = hc + " " + ht  + " " + b + " " + ey + " " + na + " " + nc
        else:
            n =  hc + " " + ht  + " " + b + " " + ey + " " + na
        
        
        lx=list(n.split(" "))
        list2=[]
        for x in mongo.db.imgatt1.find():
            a=x.get('tags')
            fp = list(a.split(" "))
            fp.remove("")
            flag=0
            count=0
            if 'Male' in lx or 'Male' in fp:
                for i in range(0,len(lx)):
                    flag=0
                    for j in range(len(fp)):
                        if lx[i] == fp[j]:
                            flag=1
                            count=count+1
                            break
                if count>=(len(fp)-2):
                    list2.append(x)
            else:
                for i in range(len(lx)):
                    flag=0
                    for j in range(len(fp)):
                        if lx[i]==fp[j]:
                            flag=1
                            count=count+1
                            break
                if count>=(len(fp)-2):
                    list2.append(x)
        return render_template('images.html', images= list2)           






@app.route('/imgupload', methods=['GET','POST'])
def imgfeatures():
    if request.method == 'GET':
        return render_template('img.html',value ="hi")
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']
        # Make prediction
        preds = model_predict(f)
        st = ""
        q = str(preds)
        n = q.split(";")
        for i in range(len(n)):
            st = st + n[i] + " "
        
        
        m = "static/uploads/" + f.filename

        mydict = { "img_path": m , "tags": st  }

        x = mongo.db.imgatt1.insert_one(mydict)
        img = cv2.imread(f.filename ,1)
        path = 'C:\\Users\\sujit\\flaskmongo\\static\\uploads'
        cv2.imwrite(os.path.join(path,f.filename),img)
        
        return render_template('result.html',pred=preds)



       
if __name__ == '__main__':
    app.run(debug = True)