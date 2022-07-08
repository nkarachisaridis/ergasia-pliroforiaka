from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, Response, jsonify ,session ,render_template
import json

import uuid
import flask
import datetime

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose InfoSys database
db = client['DigitalNotes']
usersColl = db['users']
notesColl = db['notes']

# Initiate Flask App
app = Flask(__name__, template_folder='template')  
app.secret_key = 'nikolas'

@app.route('/delete_Admin/', methods=['GET','POST'])
def delete_Admin():
    
     if request.method =='GET':
       
        return render_template('delete_Admin.html')
        
     elif request.method == 'POST':
        
        if '_id' and 'role' in session:
            if session['role'] == '0' :
                return 'No permitted access'
            elif session['role'] == '1' :      
                if usersColl.find_one({'username': request.form['username']}):
                    myquery = { 'username': request.form['username'], 'user_Id':session['_id'] }
                    usersColl.delete_one(myquery)
               
                    return 'Deleted user'
                else:
                    return 'No user found'
                         
 
   
@app.route('/Insert_Admin/', methods=['GET','POST'])
def Insert_Admin():
    if request.method =='GET':
       
        return render_template('Insert_Admin.html')
        
    elif request.method == 'POST':
      
        if '_id' and 'role' in session:
            if session['role'] == '0' :
                return 'No permitted access'
            elif session['role'] == '1' :
        
                if usersColl.find_one({'username': request.form['username']}) and usersColl.find_one({'email': request.form['mail']})  :
                    return 'User Exist try something else'
                else:
                    user={
                    '_id':str(uuid.uuid4()),
                    'email': request.form['mail'],
                    'username': request.form['username']  ,
                    'password': request.form['password'],
                    'inserted':'0',        
                    'role': '1'
                    }
        
                    usersColl.insert_one(user)
                    return 'Inserted Admin succefully',200
        else:
            return 'No permitted access'                  
        
        


    
@app.route('/CreateNote/', methods=['GET','POST'])
def CreateNote():

    if request.method =='GET':
       
        return render_template('CreateNote.html')
        
    elif request.method == 'POST':

        
        if '_id' in session:

            
            
            if notesColl.find_one({'title':request.form['title'],'user_Id':session['_id']}):
                return 'You have already have this Note'
            else:
                Notes={
                '_id': str(uuid.uuid4()),
                'user_Id': session['_id'],
                'title': request.form['title'],
                'text': request.form['text']  ,
                'tags': request.form['tags'],
                'time': datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                 }
                notesColl.insert_one(Notes)

                return 'Succefuly Created Note'    
      
        else:
            return 'No permited access'
        
    
@app.route('/ttl_Search/', methods=['GET','POST'])
def ttl_Search():
    if request.method =='GET':
       
        return render_template('ttl_Search.html')
        
    elif request.method == 'POST':
        if '_id' in session:
            AllNotes = notesColl.find(notesColl.find_one({'title': request.form['ttl'],'user_Id':session['_id']}))
            return flask.jsonify([notes for notes in AllNotes])
        else:
            return 'No permitted access'
        
    
@app.route('/tag_Search/', methods=['GET','POST'])
def tag_Search():
    if request.method =='GET':
       
        return render_template('tag_Search.html')
        
    elif request.method == 'POST':
        if '_id' in session:
  
            AllNotes = notesColl.find(notesColl.find_one({'tags': request.form['tag'],'user_Id':session['_id']}))
            return flask.jsonify([notes for notes in AllNotes])
        
    
        else:
            return 'No permitted access'
        
 
@app.route('/delete_Note/', methods=['GET','POST'])
def delete_Note():
    
    if request.method =='GET':
        return render_template('delete_Note.html')
        
    elif request.method == 'POST':
    
    
        if '_id' in session:
        
        
            if  notesColl.find_one({'title': request.form['title'],'user_Id':session['_id']}):

                myquery = { 'title': request.form['title'],'user_Id':session['_id'] }
                notesColl.delete_one(myquery)
                return 'Deleted Note'
            else:
                return '0 Notes with this title'     
        else:
            return 'Login first'           
                      
 
@app.route('/sort/', methods=['GET','POST'])
def sort():
    if request.method =='GET':
        return render_template('sort.html')
        
    elif request.method == 'POST':
       
        if '_id' in session:
            if request.form['sort'] == 'ascending':
                AllNotes = notesColl.find({'user_Id':session['_id']}).sort('time',+1)
                return flask.jsonify([notes for notes in AllNotes])
            elif request.form['sort'] == 'descending' :
                AllNotes = notesColl.find({'user_Id':session['_id']}).sort('time',-1)
                return flask.jsonify([notes for notes in AllNotes])
            else :    
                return render_template('sort.html')
        else:
            return 'Login first'        
               
 
@app.route('/Update_Note/', methods=['GET','POST'])
def Update_Note():
    if request.method =='GET':
        return render_template('Update_Note.html')
    elif request.method == 'POST':
        if '_id' in session:
            if  notesColl.find_one({'title':request.form['title'] ,'user_Id':session['_id']} ) :
                if request.form['new_text']:
                    new_text= request.form['new_text']
                else:
                    txt=notesColl.find_one({'title':request.form['new_text'] },{'_id':0,'text':1})
                    new_text=txt['text']
                if request.form['new_tags']:
                    new_tags= request.form['new_tags']
                else:
                    tag=notesColl.find_one({'title':request.form['title']},{'_id':0,'tags':1})
                    new_tags=tag['tags']
                if request.form['new_title']:
                    new_title= request.form['new_title']
                else:
                   tlt=notesColl.find_one({'title':request.form['title'] },{'_id':0,'title':1})
                   new_title =tlt['title']
                notesColl.update_many({'title': request.form['title']},{'$set': {'title':new_title,'text': new_text ,'tags':new_tags}})
                return notesColl.find_one({'title': request.form['new_title'],'user_Id':session['_id']}),200
            else:  
                return '0 Notes with this title '
        else:
            return 'Not permitted access'
               
               
            
   
@app.route('/delete/', methods=['GET','POST'])
def delete():
    if '_id' in session:
        myquery = { '_id': session['_id'] }
        usersColl.delete_one(myquery)
        session.pop('_id', None)
        session.pop('role', None)
        return 'Deleted' 
    else:
        return 'No permitted access'        



@app.route('/Updatepassword/', methods=['GET','POST'])
def Updatepassword():
    if '_id' in session:
    
        filter = { 'inserted': '0' }
        newvalues = { "$set": { 'inserted': '1' } }
        usersColl.update_one(filter, newvalues)
        
        return 'Succesfully Update'       
               
    else:
        return 'No permited access'
                      
       

@app.route('/login/', methods=['GET','POST'])

def login():
    if request.method =='GET':
        return render_template('login.html')
        
    elif request.method == 'POST':
        
        user=usersColl.find_one({'username': request.form['username']})
        password=usersColl.find_one({'password': request.form['password']})
        mail=usersColl.find_one({'email': request.form['mail']})
        
        if (user and password)  and (mail and password) :
           
            Id_tmp = usersColl.find_one({'username': request.form['username'],'password': request.form['password'],'email': request.form['mail']},{'_id':1 }) 
            Id_tmp=Id_tmp['_id']
            role_tmp = usersColl.find_one({'username': request.form['username'],'password': request.form['password'],'email': request.form['mail']},{'_id':0 ,'role':1})
            role_tmp=role_tmp['role']
            inserted_tmp= usersColl.find_one({'username': request.form['username'],'password': request.form['password'],'email': request.form['mail']},{'_id':0 ,'inserted':1})          
            inserted_tmp=inserted_tmp['inserted']       
            
            session['role'] = role_tmp
            session['_id'] = Id_tmp 
            
            if inserted_tmp == '0' and role_tmp=='1':
                return render_template('Updatepassword.html')
            else:
                return 'login succesfully'       
             
        else:    
            return "Please try again something went wrong or sign up first", 500     
    

        

@app.route('/signup/', methods=['GET','POST'])
def signup():
    if request.method =='GET':
        return render_template('Signup.html')
        
    elif request.method == 'POST':
        if usersColl.find_one({'username': request.form['username']}) and usersColl.find_one({'email': request.form['mail']})  :
            return 'This username or email have been already in use, try something else'
        else:
            user={
            '_id':str(uuid.uuid4()),
            'email': request.form['mail'],
            'username': request.form['username']  ,
            'name': request.form['name'],
            'password': request.form['password'],
            'inserted':'1',
            'role': '0',
            
            }
        
            usersColl.insert_one(user)
            return 'You have registered successfully',200     
        
        
        
        
    
# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
