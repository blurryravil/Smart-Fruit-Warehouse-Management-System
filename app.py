from flask import Flask, render_template
from requests import request
import pickle
import json
import csv
import urllib.request
import numpy as np
import pandas as pd
import seaborn as sns
import ast
data1 = urllib.request.urlopen('https://api.thingspeak.com/channels/1784550/fields/1.json?api_key=W1TUMWD9WMVX4UX6&results=10')
read1 = data1.read()
data3 = urllib.request.urlopen('https://api.thingspeak.com/channels/1784550/fields/3.json?api_key=W1TUMWD9WMVX4UX6&results=10')
read3 = data3.read()
temp=ast.literal_eval(read1.decode('utf-8'))
gas=ast.literal_eval(read3.decode('utf-8'))
list1 = []
for i in range(0,10):
    list1.append(float(gas['feeds'][i]['field3']))
final_gas=sum(list1)/10
if final_gas<=130:
    grade = 1
elif final_gas<=210:
    grade = 2
elif final_gas<=360:
    grade = 3
else:
    grade = 4
app = Flask(__name__,template_folder='templates')
model = pickle.load(open('Model.pkl','rb'))
temp_f = float(temp['feeds'][0]['field1'])
predicted = model.predict([[temp_f,final_gas]])
time_read = predicted  
buffer_time = 0
if (grade == 1):
    dic = {'Temperature':[32.56],'Gas':[130]}
    dff = pd.DataFrame.from_dict(dic)
    time_next = model.predict(dff)[0]
    buffer_time = time_next - time_read
elif (grade == 2):
    dic = {'Temperature':[32.56],'Gas':[210]}
    dff = pd.DataFrame.from_dict(dic)
    time_next = model.predict(dff)[0]
    buffer_time = time_next - time_read
elif (grade == 3):
    dic = {'Temperature':[33.56],'Gas':[360]}
    dff = pd.DataFrame.from_dict(dic)
    time_next = model.predict(dff)[0]
    buffer_time = time_next - time_read
sample = 'Current Gas Value is {} and temperature value is {}'.format(final_gas,temp_f)
@app.route('/',methods = ['GET']) 
def home():
    return render_template('index.html')
temp = float(buffer_time[0])
@app.route('/predict',methods = ['POST','GET'])
def predict():
    if(grade == 4):
        return render_template('index.html',prediction_text='{}. Your fruit is in Grade 4. It has been rotten.'.format(sample))
    else:
        return render_template('index.html',prediction_text='{}. Your fruit is currently in Grade {}.Time left for it to degrade to Grade {} is {:.2f} hours.'.format(sample,grade,grade+1,temp))
if __name__ == '__main__':
    app.run(debug=True)
