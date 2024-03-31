from bson import ObjectId
from flask import Flask, redirect, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
from icecream import ic

from os import environ

load_dotenv()

app = Flask(__name__)
client = MongoClient(environ.get('MONGODB'))
db = client["Microblog"] 
entries_collection = db.entries

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        content = request.form.get('content')
        if content:
            formatted_date = datetime.datetime.today().strftime("%b %d, %I:%M %p")
            entries_collection.insert_one({"content": content, 
                                           "date": formatted_date, 
                                           "pinned":0})
            ic("Content inserted", request.method)
            return redirect('/')
    
    entries = get_entries()
    return render_template('home.html', entries=entries)



@app.route('/delete/<id>')
def delete(id):
    deleted = entries_collection.delete_one({"_id": ObjectId(id)})
    ic(deleted)
    return redirect('/')

@app.route('/pin/<id>')
def pin(id):
    pinned = entries_collection.update_one({"_id":ObjectId(id)}, {"$inc":{"pinned":1}})
    ic(pinned)
    return redirect('/')

@app.route('/edit/<id>',methods=["GET","POST"])

def edit(id):

    entry = entries_collection.find_one({"_id":ObjectId(id)})
    ic(entry)
    if request.method == "POST":
        ic(request.form.get("content"))
        entries_collection.find_one_and_update({"_id":ObjectId(id)},{"$set":{"content":request.form.get("content")}})
        return redirect('/')
    return render_template('edit.html',entry=entry['content'])

def get_entries():
    """
    Retrieves all entries from the entries collection and returns them in reverse chronological order.

    Returns:
        list: A list of dictionaries containing the 'content', 'date', and 'id' fields of each entry.
    """
    entries_cursor = entries_collection.find({})
    entries = [
        {
            "content": entry['content'],
            "date": entry['date'],
            "id": entry['_id'],
            "pinned":entry['pinned']
        }
        for entry in entries_cursor
    ]
    entries.sort(key=lambda x: x['pinned'])
    ic(entries)
    return entries[::-1]

if __name__ == "__main__":
    app.run(debug=True, port=8080)
