from bson import ObjectId
from flask import Flask, redirect, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
from icecream import ic
from bleach import clean,linkify

from bleach import callbacks


from os import environ

load_dotenv()

app = Flask(__name__)
client = MongoClient(environ.get('MONGODB'))
db = client["Microblog"] 
entries_collection = db.entries
deleted_collection = db.deleted


def custom_linkify(attrs,new=False):
    attrs[(None,"class")] = 'postlink'
    return attrs


def sanitize(content):
    safe_content = clean(content)
   
    linkified_content = linkify(
        safe_content,
        callbacks=[callbacks.nofollow,callbacks.target_blank,custom_linkify])
    return linkified_content


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        content = request.form.get('content')
        content = sanitize(content) # for security measures
        if content:
            formatted_date = datetime.datetime.today().strftime("%b %d, %I:%M %p")
            entries_collection.insert_one({"content": content, 
                                           "date": formatted_date, 
                                           "pinned":0})
          
            return redirect('/')
    
    entries = get_entries()
    return render_template('home.html', entries=entries)



@app.route('/deleted')
def deleted():
    all_entries =  get_deleted_entries() #everything in the deleted collection
    entries = [entry for entry in all_entries if entry['time_left'] > 0] # entries that still have remaining time
    entries_to_delete = [entry["_id"] for entry in all_entries if entry not in entries] #entries that should be permenantly deleted
    for entry in entries_to_delete:
        deleted_entry = deleted_collection.delete_one({"_id":entry})
        ic(deleted_entry)

  
    return render_template('deleted.html',entries = entries)




@app.route('/recover/<id>')
def recover(id):
    post = deleted_collection.find_one({"_id":ObjectId(id)})
    deleted = deleted_collection.delete_one(post)
    post["content"] = f"{post['content']} <br> ================RECOVERED==============="
    entries_collection.insert_one(post)

    
    return redirect('/')

@app.route('/delete/<id>')
def delete(id):
    # adding the deleted post to the recently deleted collection
    post = entries_collection.find_one({"_id":ObjectId(id)})
    post["date"] = datetime.datetime.today().strftime("%b %d")
    deleted_collection.insert_one(post)

    deleted = entries_collection.delete_one({"_id":ObjectId(id)})
    return redirect('/')



@app.route('/pin/<id>')
def pin(id):
    pinned = entries_collection.update_one({"_id":ObjectId(id)}, {"$inc":{"pinned":1}})
    ic(pinned)
    return redirect('/')

@app.route('/decrease-pin/<id>')
def decrease_pin(id):
    entries_collection.update_one({'_id':ObjectId(id)},{"$inc":{"pinned":-1}})
  
    return redirect('/')

@app.route('/edit/<id>',methods=["GET","POST"])
def edit(id):

    entry = entries_collection.find_one({"_id":ObjectId(id)})
    ic(entry)
    if request.method == "POST":
        ic(request.form.get("content"))
        entries_collection.find_one_and_update({"_id":ObjectId(id)},{"$set":{"content":sanitize(request.form.get("content"))}})
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
    if entries:
        entries.sort(key=lambda x: x['pinned'])
        print(entries[0]['content'])
        return entries[::-1]
    return entries



def get_deleted_entries():
    entries_cursor = deleted_collection.find({})
    today = datetime.datetime.today()

    deleted_entries = [
        {
          '_id':entry['_id'],
          'content':entry['content'],
          'pinned':entry['pinned'],
          'days_since_deletion':(today - (datetime.datetime.strptime((entry['date'].split(',')[0]),"%b %d")).replace(year=today.year)).days,
          'time_left':3 - (today - (datetime.datetime.strptime((entry['date'].split(',')[0]),"%b %d")).replace(year=today.year)).days
        }
        
        for entry in entries_cursor
    ]
   
   
    return deleted_entries
get_deleted_entries()
if __name__ == "__main__":
    app.run(debug=True, port=8080,host='0.0.0.0')
