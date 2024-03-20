
from pymongo import MongoClient

client = MongoClient("mongodb+srv://yassinwaelmohamed84:BuDWEJMQKOFx1mYx@microblog.8kjr3ri.mongodb.net/")
db = client["Microblog"] 
collection = db["entries"]

entries = []

list_ = (list(db.entries.find({})))

entries_list = [
    {
        "content":content['content'],
        "date":content['date']
    }
    for content in list_
]

print(entries_list)