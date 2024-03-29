from bson import ObjectId
from flask import Flask, redirect,render_template,request,url_for
from pymongo import MongoClient
import datetime
from icecream import ic
from dotenv import load_dotenv
from os import environ
load_dotenv()

app = Flask(__name__)
client = MongoClient(environ.get('MONGODB'))
app.db = client["Microblog"] # makes a test database called "testdb"
collection = app.db.entries

entries = []
# vercel
@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])

def home():
    
    if request.method == "POST":
        content = request.form['content']
        formatted_date = datetime.datetime.today().strftime("%b %d, %I:%M %p")
        app.db["entries"].insert_one({"content":content,"date":formatted_date})
        ic("content inserted",request.method)
        return redirect(url_for('home'))
    

    entries = [
             {
        "content":entry['content'],
        "date":entry['date'],
        "id": entry['_id']
             }
            for entry in list(app.db.entries.find({}))
        ]
       
 

    return render_template('index.html',entries=entries)



@app.route('/delete/<id>')
def delete(id):
    ic(id)
    deleted = collection.delete_one({"_id": ObjectId(id)})
    ic(deleted)
    return redirect(request.referrer)




app.run(debug=True,host='0.0.0.0',port=8080)