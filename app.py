# from tkinter import INSERT
# from email.policy import default
# import default as default
#import cv2
import app as app
from flask import Flask, render_template, flash, request, redirect, url_for, session, logging, send_from_directory,flash,Response
#from flask_datepicker import datepicker
from wtforms.fields.html5 import DateField
# from data import Articles
# Articles=Articles()
# For seraching category
from app import app

from wtforms import Form, StringField, TextAreaField, validators, PasswordField, BooleanField, DateField, SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mail import Mail, Message
import cx_Oracle
import os
con = cx_Oracle.connect('doner/doner@//localhost:1521/orclpdb')
#con = cx_Oracle.connect('doner/doner@localhost/Orcl')
#con = cx_Oracle.connect('oriondb/o@118.67.215.114/Orcl')


#print(con.version)

APP_ROOT = os.path.dirname(os.path.abspath(__file__)) ##It is store the image in the pycharm enginee.

#APP_ROOT='E:\image' #this path store the image in desktop E image folder;
#print(APP_ROOT)
#print(1111)

app = Flask(__name__)
#Python web streaming code
#camera=cv2.VideoCapture(0)
# first Articles is the name of variables and second is the created function name Articles()
app.config['UPLOAD_FOLDER'] = APP_ROOT
print(APP_ROOT)
# Configure Email
app.config.update(
    dict(
        DEBUG=True,
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME="espiputul@gmail.com",
        MAIL_PASSWORD='baizeed01714730166///'
    )
)

mail = Mail(app)



# Register Form Class
class RegistrationForm(Form):
    name = StringField('name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    mothersname = StringField('mothers name', [validators.Length(min=4, max=25)])
    phone = StringField('Mobile No:')
    bloodgroup = StringField('blood group')
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    district = StringField('District')
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Rpt Password')
    last_donate_date=DateField('last_donate_date')
    # image = ('upload'), format='%d/%m/%y',validators=(validators.DataRequired(),))
    # accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


@app.route('/')
def index():
    return render_template("home.html")

# About
@app.route('/about')
def about():
    return render_template("about.html")


# Articles
@app.route('/articles')
def articles():
    cur = con.cursor()
    result = cur.execute('select * from articles')
    articles = cur.fetchall()
    # data = cur.fetchone()
    if result.rowcount > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = ('No articles')
        return render_template('articles.html', msg=msg)
    # return render_template("articles.html", articles = Articles)


# Single Article
@app.route('/article/<string:id>/')
def article(id):
        cur = con.cursor()

        cur.execute("select * from articles where id='{}'".format(id))
        article = cur.fetchone()

        return render_template('article.html', article=article)


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    #print(request.form)
    form_response = RegistrationForm(request.form)
    if request.method == 'POST' and form_response.validate():
        name = form_response.name.data
        username = form_response.username.data
        mothersname = form_response.mothersname.data
        phone = form_response.phone.data
        email = form_response.email.data
        bloodgroup = form_response.bloodgroup.data
        district = form_response.district.data
        password = sha256_crypt.encrypt(str(form_response.password.data))
        last_donate_date=form_response.last_donate_date.data
        # image = form_response.image.data
        cur = con.cursor()
        # https://learncodeshare.net/2015/06/26/insert-crud-using-cx_oracle/ inserting documentations
        cur.execute("INSERT INTO users (name, username, mothersname, phone, email, bloodgroup, DISTRICT,password,last_donate_date)"
                    " VALUES (:name, :username, :mothersname, :phone, :email, :bloodgroup, :district,:password,:last_donate_date)",
                    (name, username, mothersname, phone, email, bloodgroup, district,password,last_donate_date))
        # alternate code
        #cur.execute("INSERT INTO users (name, username, mothersname, phone, email, bloodgroup, DISTRICT,password)"
                    #" VALUES (\'{}\',\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')".
                   # format(name, username, mothersname, phone, email, bloodgroup, district, password))



        con.commit()
        # return "<h1>You are now registered</h1>"
        flash("you are now registered", "success")
        return redirect(url_for("login"))

        # return render_template('register.html')
    return render_template('register.html', form=form_response)


# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # get forms field
        username = request.form['username']
        password_candidate = request.form['password']
        # create cursor
        cur = con.cursor()
        # https://learncodeshare.net/2015/06/26/insert-crud-using-cx_oracle/ creating cursor in python
        result = cur.execute("select password from users where username = '{}'".format(username))
        data = cur.fetchone()
        if result.rowcount > 0:
            password = data[0]
            # create password

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('you are logged in,success')
                return redirect(url_for('dashboard'))
                # if user logged in then it will go to another page dashboard
                app.logger.info('password matched')
                return "<h1>password matched</h1>"
            else:
                app.logger.info('no user')
                return "<h1>Password not matched</h1>"

        else:
            return "<h1>user not match</h1>"

    return render_template('login.html')


# Check if user logged_in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('unauthorised ,please loggin')
            return redirect(url_for('login'))
    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("you are logged out")
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = con.cursor()
    result = cur.execute('select * from articles')
    articles = cur.fetchall()

    # data = cur.fetchone()
    if result.rowcount > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = ('no articles found')
        return render_template('dashboard.html', msg=msg)


class ArticleForm(Form):
    title = StringField('title', [validators.Length(min=4, max=50)])
    body = TextAreaField('body', [validators.Length(min=4)])
    author = StringField('author')
    file_name = StringField('file_name')


# add article
@app.route('/add_article', methods =['POST','GET'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    ##This code will generate the image path and strore the image ##
    if request.method == 'POST' and form.validate():
        target = os.path.join(APP_ROOT, 'static')
        if not os.path.isdir(target):
            os.mkdir(target)
        if 'file' not in request.files:
            flash("No file")
            return render_template('upload.html')
        filename = request.files['file']

        print(request.files)
        print(111111111)

        filename.save(os.path.join(target, filename.filename))
        print(filename.filename)
        print(33333333)

        ##end code##
        title = form.title.data
        body = form.body.data
        author = session['username']
        file_name=filename.filename  ##



# create cursor
        cur = con.cursor()
        cur.execute("insert into articles(title,body,author,file_name)VALUES (\'{}\',\'{}\',\'{}\',\'{}\')".
                    format(title, body, author,file_name))
        con.commit()

        flash("Articles created successfully")
        return redirect(url_for('dashboard'))
    return render_template('add_article.html',form=form)


# Edit article
@app.route('/edit_article/<string:id>',methods =['POST','GET'])
@is_logged_in
def edit_article(id):
    # create cursor
    cur = con.cursor()

    # Get Article
    cur.execute("select * from articles where id='{}'".format(id))
    article = cur.fetchone()
    # Get Form
    form = ArticleForm(request.form)

    # populate article form fields

    # title = form.title.data
    # body = form.body.data
    if request.method == 'GET':
        form.title.data = article[1]
        form.body.data = article[3]

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data


# create cursor
        cur = con.cursor()

        # Execute
        cur.execute("update articles set title='{}',body='{}' where id='{}'".format(title, body, id))
        con.commit()

        flash("Articles updated successfully")
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)


# Delete Article
@app.route('/delete_article/<string:id>', methods=['post'])
def delete_article(id):

        # create cursor
        cur = con.cursor()

        # Execute Cursor
        cur.execute("delete from articles where id='{}'".format(id))
        con.commit()

        flash('article delete successfully', 'success')
        return redirect(url_for('dashboard'))


# User_list
@app.route('/user_list')
@is_logged_in
def user_list():

    cur = con.cursor()
    result = cur.execute('select * from users order by bloodgroup desc')
    users = cur.fetchall()
    directory = os.path.join(APP_ROOT, 'images')
    image_path = os.path.join(directory, 'cat.jpg')
    # print(image_path)
    # data = cur.fetchone()
    if result.rowcount > 0:
        return render_template('user_list.html',users= users, user_image =image_path)
    else:
        msg = ('no user found')
        return render_template('user_list.html', msg = msg)


# Old system of  image uploading
'''@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    if request.method == 'POST':
        target = os.path.join(APP_ROOT, 'images/')
        if not os.path.isdir(target):
            os.mkdir(target)
        if 'file' not in request.files:
            flash("No file")
            return render_template('upload.html')
        upload_file = request.files['file']
        upload_file.save(os.path.join(target, upload_file.filename))
        flash('file uploaded successfully')

        return render_template('upload.html')
        # return render_template('complete.html', image_name=filename)'''


# New system of  purpose image handling
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')


    if request.method == 'POST':
        target = os.path.join(APP_ROOT, 'images')
        if not os.path.isdir(target):
            os.mkdir(target)
        if 'file' not in request.files:
            flash("No file")
            return render_template('upload.html')
        filename = request.files['file']
        filename.save(os.path.join(target, filename.filename))


##for uploading image url in database this code
        cur = con.cursor()
        cur.execute("insert into image_load(  image_url)VALUES (\'{}\')".
                    format( filename.filename))
        con.commit()
# End code

        flash('file uploaded successfully')

        return render_template('upload.html',image_name=filename)
        # return render_template('complete.html', image_name=filename)
print(upload)

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images",filename)
print(send_image)


@app.route('/gallery')
def get_gallery():
    image_names = os.listdir('./images')
    return render_template('gallery.html', image_names=image_names)
print(get_gallery)

'''
@app.route('/account')
def account():
    image_file = url_for('images', file_name='cat.jpg')
    return render_template('account.html')
'''


# Mail form class
'''class MailForm(Form):
    email = StringField('Email Address')
    # accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])'''


# Send Email message
@app.route('/message/<receiver>', methods=['GET'])
def message(receiver):
      msg = Message("Hello Rony",
              sender="espiputul@gmail.com",
              recipients=[receiver])
      msg.body='it is a test message'
      msg.html="<b>Hello it is a test message</>"
      mail.send(msg)
      return 'message sent'
      # return redirect(url_for('message'))
      print(msg.html)
# return render_template('message.html', msg=msg)
      flash('email sent successfully')


'''@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)'''


# Search Class


class SearchForm(Form):
    choices = [('bloodgroup','bloodgroup')]
    select=SelectField('Search For Blood', choices=choices)
    search = SelectField('search', choices=[('AB+', 'AB+'), ('B+', 'B+'),('A+', 'A+')])
    # search=StringField('')


# Search Items
@app.route('/search', methods=['GET', 'POST'])
# create_cursor
def search():
    search=SearchForm(request.form)
    if request.method=='POST':
        return search_results(search)
    return render_template('search.html', form=search)


@app.route('/results')
def search_results(search):
    search_string = search.data['search']
    if search_string:
        if search.data['select'] == 'bloodgroup':
            cur = con.cursor()
        cur.execute('''select * from users where bloodgroup = :bloodgroup''', bloodgroup=search_string)
        results = cur.fetchall()

    if not results:
        flash('No results found!ha ha ha')
        return redirect('search.html')
    else:
        return render_template('results.html', results=results)


# Blog list
@app.route('/bloglist')
def bloglist():

    article_image_names = os.listdir('./images')


    # for  right side div function
    cur = con.cursor()
    results = cur.execute(''' select *from ARTICLE_2''')


    allblog = cur.fetchall()





    # end right side div function

# for left side div function
    cur = con.cursor()
    oneresult = cur.execute('''select * from article''')
    onse = cur.fetchall()

    # cur.execute('''select file_name from article''')
    # onseimage = cur.fetchall()
    # print(onseimage)
    # print(1111111111111111)
    # print(article_image_names)




    # if article_image_names == onseimage:
    #     finalimage=article_image_names
    # else:
    #     return 'No results found!ha ha ha'

    # end left side
    if results.rowcount > 0 or oneresult.rowcount > 0:
        return render_template('bloglist.html', bloglists=allblog,onse=onse,finalimage=article_image_names)
    else:
        msg = ('no data found')
        return render_template('bloglist.html', msg=msg)



# Flask Crud application full course
class employeedata(Form):
    EMPLOYEE_NAME = StringField('EMPLOYEE_NAME', [validators.Length(min=4, max=25)])
    EMAIL = StringField('EMAIL', [validators.Length(min=4, max=25)])
    PHONE_NUMBER = StringField('PHONE_NUMBER', [validators.Length(min=4, max=25)])
print(employeedata)


@app.route('/employee')
def employee():
    cur = con.cursor()
    result = cur.execute('select * from employee order by employee_id')
    return render_template('employee.html',result=result)


@app.route('/insert',  methods=['POST','GET'])
def insert():
    print(0)
    form_response = employeedata(request.form)
    print(1)
    if request.method == 'POST' and form_response.validate():
        print(2)
        EMPLOYEE_NAME = form_response.EMPLOYEE_NAME.data
        EMAIL=form_response.EMAIL.data
        PHONE_NUMBER=form_response.PHONE_NUMBER.data
        print(3)
        cur = con.cursor()
        print(4)
        cur.execute(
            "INSERT INTO employee (EMPLOYEE_NAME, EMAIL, PHONE_NUMBER)"
            " VALUES (:EMPLOYEE_NAME,  :EMAIL,:PHONE_NUMBER)",
            (EMPLOYEE_NAME,  EMAIL,PHONE_NUMBER))
        print(5)
        con.commit()
        flash("Employee Has Been Added Successfully", "success")
        #return render_template('employee.html', form=form_response)
        return redirect(url_for('employee'))
    else:
        print(form_response.validate())
        print(7)
        # redirect(url_for('employee.html'))
        return render_template('employee.html', form=form_response)
    print(8)
    # redirect(url_for('employee.html'))
    print(9)


#Python web streaming code
def generate_frames():
    while True:
        ## read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/VideoStreaming')
def VideoStreaming():
    return render_template('VideoStreaming.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


## End Web Streaming code ##



## Start coading the image url upload in the database and image in the local folder ##




if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(debug=True)

    # below code is for ip setting.
    # app.run(host="192.168.0.106")
