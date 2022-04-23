import os
from time import sleep
from flask import Flask, jsonify, request, render_template
from firebase_admin import credentials, firestore, initialize_app
import requests


# Initialize Flask App
app = Flask(__name__)
# Initialize Firestore DB
cred = credentials.Certificate('upidata-f23a4-firebase-adminsdk-fxqed-e1e9866762.json')
default_app = initialize_app(cred)

@app.route('/')
def welcome():    
    try: 
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        return render_template('index.html', data=jsonify(all_todos)),200
    except Exception as e:
        return f"An Error Occured: {e}"

db = firestore.client()
todo_ref = db.collection('applications')
    

@app.route('/add', methods=['POST'])
def create():
    """
        create() : Add document to Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    try:
        id = request.json['Serial Number']
        todo_ref.document(str(id)).set(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents
    """
    try:
        # Check if ID was passed to URL query
        todo_id = request.args.get('id')    
        if todo_id:
            todo = todo_ref.document(todo_id).get()
            return jsonify(todo.to_dict()), 200
        else:
            all_todos = [doc.to_dict() for doc in todo_ref.stream()]
            return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a collection from Firestore collection
    """
    try:
        # Check for ID in URL query
        # todo_id = request.args.get('id')
        # todo_ref.document(todo_id).delete()
        delete_collection(todo_ref, 100)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
