import json
import pandas as pd
import re
from os.path import basename
from urllib.request import urlopen
import time
import psycopg2 #convert python variable to sql variable
import os
import csv
import requests #for requesting Api
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import config
app = Flask(__name__)

filename1 = ""   #global variables define to access in whole program
link = ""
path1 = ""
fname1 = ""
table1 = "table1"
rowcount = "0"
#config commenting in form of algo
#naming convention

#Create engine in postgresql for further process.
try:
    engine = create_engine('postgresql://'+config.user+':'+config.password+'@localhost:5432/'+config.database)
    #Create a pyscog connection so that python variable is converted to sql variable.
    conn = psycopg2.connect(host="localhost",database=config.database,user = config.user, password=config.password)
    cur = conn.cursor()
except:
    print("Error while creating database ")

@app.route('/',methods=["GET","POST"])
def loadfile():
    #defining global variable to store value in global instead of local variable
    global filename1
    #defining global variable to store value in global instead of local variable for the link
    global link
    global path1
    global fname1
    global cur
    global table1
    global rowcount
    if request.method == 'GET':
        #CHECK If request method is get render the page i.e when upload button is clicked#
        return render_template('home.html')
    if request.method == 'POST':
        if request.form.get("link") is not None and request.form.get("link") is not '':
            link = request.form.get('link')
            r = requests.get(request.form.get("link"))    #request the link
            fname = link[link.rfind("/")+1:]
            fname1 = fname[:-4].lower()
            extension = fname[-4:].lower()
            if extension == ".csv":
                path1 = "./static/"+table1
                #Filedir = os.path.join(BASE_DIR,path1)
                f= open(path1,"w+") #write the data in file.
                with open(path1,'wb') as f:
                    f.write(r.content)
                link = request.form.get("link")
                cur = conn.cursor()
                with open(path1,'r') as f:
                    headervalue = []
                    headervalue = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalue]
                    df = pd.read_csv(link)
                    df.columns = df.columns.str.strip()
                    #find the length of the panda frame.
                    rowcount = len(df)
                    #pass table name to_sql to create the table with index true as primary key,if_exists field to delete table if exist.
                    df.to_sql("table1", engine, index=True,if_exists=u'replace')
                return redirect(url_for('home'))
            else:
                return "Invalid Csv"
        elif request.files['file'] is not None and request.files['file'] is not '':
            #Check if request method is post send the data to addrecord.html for further process.
            filename = request.files['file'] #request filename path.
            filename1 = filename.filename #request filename name i.e name.csv or else.
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #create a absolute path
            path = "Assignment2/static/"+filename.filename #map the filename with assignment2 folder and make file in static.
            Filedir = os.path.join(BASE_DIR,path)
            with open(Filedir, 'r') as f:
                #empty list to store file header.
                headervalue = []
                #split list by , as delimeter
                headervalue = next(f).split(',')
                #remove \n from the end of the header i.e id , name , email\n
                strippedline = [s.rstrip() for s in headervalue]
                #remove the space in header
                strippedline = [s.replace(" ","") for s in strippedline]
                #read the file and store it in panda frame.
                df = pd.read_csv(Filedir)
                df.columns = df.columns.str.strip()
                #find the length of the panda frame.
                rowcount = len(df)
                #pass table name to_sql to create the table with index true as primary key,if_exists field to delete table if exist.
                df.to_sql("table1", engine, index=True,if_exists=u'replace')
            return redirect(url_for('home'))


#************************************************home page to display data when form is submitted ************************
@app.route('/home')
def home():
    global filename1
    global link
    global path1
    if filename1 is not None and filename1 is not '':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #create a absolute path
        path = "Assignment2/static/"+filename1 #map the filename with assignment2 folder and make file in static.
        Filedir = os.path.join(BASE_DIR,path)
        with open(Filedir, 'r') as f:
            #empty list to store file header.
            headervalue = []
            #split list by , as delimeter
            headervalue = next(f).split(',')
            #remove \n from the end of the header i.e id , name , email\n
            strippedline = [s.rstrip() for s in headervalue]
            #remove the space in header
            strippedline = [s.replace(" ","") for s in strippedline]
            # print(strippedline)
            cur.execute("select * from table1;")
            indexvalue = [list(r) for r in cur.fetchall()]
            conn.commit()
        return render_template('addrecord.html',collen = len(strippedline), header = strippedline,indexval = indexvalue)
    elif link is not None and link is not '':
        with open(path1, 'r') as f:
            #empty list to store file header.
            headervalue = []
            #split list by , as delimeter
            headervalue = next(f).split(',')
            #remove \n from the end of the header i.e id , name , email\n
            strippedline = [s.rstrip() for s in headervalue]
            #remove the space in header
            strippedline = [s.replace(" ","") for s in strippedline]
            # print(strippedline)
            cur.execute("select * from table1;")
            indexvalue = [list(r) for r in cur.fetchall()]
            conn.commit()
        return render_template('addrecord.html',collen = len(strippedline), header = strippedline,indexval = indexvalue)



#*********************************************Search function to perform search of the query.*******************************
#find the search value
@app.route('/find')
def find():
    global filename1
    global link
    global path1
    if filename1 is not None and filename1 is not '':
        #access the path of file
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = "Assignment2/static/"+filename1
        Filedir = os.path.join(BASE_DIR,path)
        with open(Filedir, 'r') as f:
            headervalueues = []
            headervalueues = next(f).split(',')
            strippedline = [s.rstrip() for s in headervalueues]
            strippedline = [s.replace(" ","") for s in strippedline]
        searchval = request.args.get('searchval')
        searchfor = request.args.get('searchfor')
        query1 = "select * from table1 where CAST ( \"" + searchval +"\"as text) ILIKE '%"+searchfor+"%';"
        cur.execute(query1)
        result = [list(r) for r in cur.fetchall()]
        return render_template("addrecord.html",collen = len(strippedline) ,indexval = result, header = strippedline)
    elif link is not None and link is not '':
        with open(path1, 'r') as f:
            headervalueues = []
            headervalueues = next(f).split(',')
            strippedline = [s.rstrip() for s in headervalueues]
            strippedline = [s.replace(" ","") for s in strippedline]
        searchval = request.args.get('searchval')
        searchfor = request.args.get('searchfor')
        query1 = "select * from table1 where CAST ( \"" + searchval +"\"as text) ILIKE '%"+searchfor+"%';"
        cur.execute(query1)
        result = [list(r) for r in cur.fetchall()]
        return render_template("addrecord.html",collen = len(strippedline) ,indexval = result, header = strippedline)




#*******************Check Mode of file *********************************
@app.route('/search',methods =["POST"])
def search():
    global filename1
    global path1
    global link
    if request.method == 'POST':
        if filename1 is not None and filename1 is not '':
            #access the path of file
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = "Assignment2/static/"+filename1
            Filedir = os.path.join(BASE_DIR,path)
            #read header of the file.
            try:
                with open(Filedir, 'r') as f:
                    headervalueues = []
                    headervalueues = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalueues]
                    strippedline = [s.replace(" ","") for s in strippedline]
                searchfor = request.form.get('myInput')
                searchval = request.form.get('droplist')
                #run the query and cast it to text to perform a search
                return redirect(url_for('find',searchfor = searchfor,searchval = searchval))
            except:
                print("Link not found in mainaddress")
        elif link is not None and link is not '':
            try:
                with open(path1, 'r') as f:
                    headervalue = []
                    headervalue = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalue]
                    strippedline = [s.replace(" ","") for s in strippedline]
                searchfor = request.form.get('myInput')
                searchval = request.form.get('droplist')
                #run the query and cast it to text to perform a search
                query1 = "select * from table1 where CAST ( \"" + searchval +"\"as text) ILIKE '%"+searchfor+"%';"
                cur.execute(query1)
                result = [list(r) for r in cur.fetchall()]
                return render_template("addrecord.html",collen = len(strippedline) ,indexval = result, header = strippedline)
            except:
                print("Link not found in mainaddress")


#intermediate result to add record in database.
@app.route('/addrecord',methods =["GET","POST"])
def addresult():
    global rowcount
    global filename1
    global link
    global path1
    if request.method == 'POST':
        if filename1 is not None and filename1 is not '':
            result = request.form;
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = "Assignment2/static/"+filename1
            Filedir = os.path.join(BASE_DIR,path)        #request the filename and path and open it from there.
            with open(Filedir,'r') as f:
                headervalue = []
                value = []
                headervalue = next(f).split(',')
                strippedline = [s.rstrip() for s in headervalue]
                strippedline = [s.replace(" ","") for s in strippedline]
                for a in range(len(strippedline)):
                    value.append(request.form.get(strippedline[a]))    #get the entered value and store it in value list.
                    #flat_list = [item for sublist in value for item in sublist]    #flatten the list of list to list.
                    #run insert into command in db execute for all the value.
                print(strippedline)
                string = "INSERT INTO table1 ( \"index\",\""
                for a in range(len(strippedline)):
                    if a == len(strippedline)-1:
                        string = string  + strippedline[a] +"\")"
                    else:
                        string = string  + strippedline[a]+ "\",\""
                string1 = string + " VALUES ('"+ str(rowcount) +"','"
                for a in range(len(strippedline)):
                    if a == len(strippedline)-1:
                        string1 = string1 + value[a] + "')"
                    else:
                        string1 = string1 + value[a] + "','"
                cur.execute(string1)
                rowcount = rowcount + 1
                string = "select \""
                for a in range(len(strippedline)):
                    if a == len(strippedline)-1:
                        string = string + strippedline[a]+ "\" from table1;"
                    else:
                        string = string + strippedline[a] +"\",\""
                cur.execute(string)
                result = [list(r) for r in cur.fetchall()]
                cur.execute("select * from table1;")
                indexvalue = [list(r) for r in cur.fetchall()]
                conn.commit()
            return render_template("addrecord.html",collen = len(strippedline),header = strippedline, indexval = indexvalue)
        elif link is not None and link is not '':
            try:
                with open(path1, 'r') as f:
                    headervalue = []
                    value = []
                    headervalue = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalue]
                    strippedline = [s.replace(" ","") for s in strippedline]
                    print(strippedline)
                    for a in range(len(strippedline)):
                        value.append(request.form.get(strippedline[a]))
                    string = "INSERT INTO table1 ( \"index\",\""
                    for a in range(len(strippedline)):
                        if a == len(strippedline)-1:
                            string = string  + strippedline[a] +"\")"
                        else:
                            string = string  + strippedline[a]+ "\",\""
                    string1 = string + " VALUES ('"+ str(rowcount) +"','"
                    for a in range(len(strippedline)):
                        if a == len(strippedline)-1:
                            string1 = string1 + value[a] + "')"
                        else:
                            string1 = string1 + value[a] + "','"
                    cur.execute(string1)
                    rowcount = rowcount + 1
                    string = "select \""
                    for a in range(len(strippedline)):
                        if a == len(strippedline)-1:
                            string = string + strippedline[a]+ "\" from table1;"
                        else:
                            string = string + strippedline[a] +"\",\""
                    cur.execute(string)
                    result = [list(r) for r in cur.fetchall()]
                    cur.execute("select * from table1;")
                    indexvalue = [list(r) for r in cur.fetchall()]
                    conn.commit()
                return render_template("addrecord.html",collen = len(strippedline),header = strippedline, indexval = indexvalue)
            except:
                print("Link not found in add record function")
    if request.method == 'GET':
        success = request.args.get('check')
        print(success)
        if filename1 is not None and filename1 is not '':
            if  success == "deletevalue":
                indexval = request.args.get('key')#request.get_data()#
                print(indexval)
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                path = "Assignment2/static/"+filename1
                Filedir = os.path.join(BASE_DIR,path)
                with open(Filedir,'r') as f:
                    headervalue = []
                    editval = []
                    headervalue = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalue]
                    strippedline = [s.replace(" ","") for s in strippedline]
                cur.execute("Delete from table1 where index = '%s'"%(indexval))
                #cur.execute("Delete from table1 where index = '%s'"%(indexval))
                cur.execute("select * from table1;")
                indexvalue = [list(r) for r in cur.fetchall()]
                rowcount = rowcount -1;
                conn.commit()
                return render_template("addrecord.html",collen=len(strippedline),header = strippedline ,indexval = indexvalue)
            elif success == "editval":
                print("inside editedvalue")
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                path = "Assignment2/static/"+filename1
                Filedir = os.path.join(BASE_DIR,path)
                with open(Filedir,'r') as f:
                    headervalue = []
                    editval = []
                    headervalue = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalue]
                    strippedline = [s.replace(" ","") for s in strippedline]
                    editval.append(request.args.get('key1'))
                    editval.append(request.args.get('key2'))
                    editval.append(request.args.get('key3'))
                    editval.append(request.args.get('key4'))
                    editval.append(request.args.get('key5'))
                    editval.append(request.args.get('key6'))
                    index = request.args.get('indexval')
                    print(editval)
                    string="UPDATE table1 SET \""
                    for a in range(len(strippedline)):
                        if a == len(strippedline)-1:
                            string = string + strippedline[a] + "\" = '" + editval[a] +"' where \"index\" = '" + index +"';"
                        else:
                            string = string + strippedline[a] +"\" = '" + editval[a] +"',\""
                    cur.execute(string)
                cur.execute("select * from table1;")
                indexvalue = [list(r) for r in cur.fetchall()]
                conn.commit()
                return render_template("addrecord.html",collen=len(strippedline),header = strippedline ,indexval = indexvalue)
        elif link is not None and link is not '':
            if  success == "deletevalue":
                indexval = request.args.get('key')#request.get_data()#
                print(indexval)
                with open(path1,'r') as f:
                    headervalue = []
                    editval = []
                    headervalue = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalue]
                    strippedline = [s.replace(" ","") for s in strippedline]
                cur.execute("Delete from table1 where index = '%s'"%(indexval))
                cur.execute("select * from table1;")
                indexvalue = [list(r) for r in cur.fetchall()]
                rowcount = rowcount -1;
                conn.commit()
                return render_template("addrecord.html",collen=len(strippedline),header = strippedline ,indexval = indexvalue)
            elif success == "editval":
                with open(path1,'r') as f:
                    headervalue = []
                    editval = []
                    headervalue = next(f).split(',')
                    strippedline = [s.rstrip() for s in headervalue]
                    strippedline = [s.replace(" ","") for s in strippedline]
                    editval.append(request.args.get('key1'))
                    editval.append(request.args.get('key2'))
                    editval.append(request.args.get('key3'))
                    editval.append(request.args.get('key4'))
                    editval.append(request.args.get('key5'))
                    editval.append(request.args.get('key6'))
                    index = request.args.get('indexval')
                    print(editval)
                    string="UPDATE table1 SET \""
                    for a in range(len(strippedline)):
                        if a == len(strippedline)-1:
                            string = string + strippedline[a] + "\" = '" + editval[a] +"' where \"index\" = '" + index +"';"
                        else:
                            string = string + strippedline[a] +"\" = '" + editval[a] +"',\""
                    cur.execute(string)
                # print("Pressed Edit Button")
                cur.execute("select * from table1;")
                indexvalue = [list(r) for r in cur.fetchall()]
                conn.commit()
                #print(editedvalue)
                return render_template("addrecord.html",collen=len(strippedline),header = strippedline ,indexval = indexvalue)

if __name__ == "__main__":
    app.run(debug=True)
