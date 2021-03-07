# from tkinter import INSERT
# from email.policy import default
# import default as default
import app as app
from flask import Flask, render_template, flash, request, redirect, url_for, session, logging, send_from_directory
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
con = cx_Oracle.connect('doner/doner@localhost/Orcl')


print(con.version)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print(APP_ROOT)

app = Flask(__name__)
# first Articles is the name of variables and second is the created function name Articles()
app.config['UPLOAD_FOLDER'] = APP_ROOT
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
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    # image = ('upload')
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
        msg = ('no articles')
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
    print(request.form)
    form_response = RegistrationForm(request.form)
    if request.method == 'POST' and form_response.validate():
        name = form_response.name.data
        username = form_response.username.data
        mothersname = form_response.mothersname.data
        phone = form_response.phone.data
        email = form_response.email.data
        bloodgroup = form_response.bloodgroup.data
        password = sha256_crypt.encrypt(str(form_response.password.data))
        # image = form_response.image.data
        cur = con.cursor()
        # https://learncodeshare.net/2015/06/26/insert-crud-using-cx_oracle/ inserting documentations
        cur.execute("INSERT INTO users (name, username, mothersname, phone, email, bloodgroup, password)"
                    " VALUES (\'{}\',\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')".
                    format(name, username, mothersname, phone, email, bloodgroup, password))
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


# add article
@app.route('/add_article', methods =['POST','GET'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']


# create cursor
        cur = con.cursor()
        cur.execute("insert into articles(title,body,author)VALUES (\'{}\',\'{}\',\'{}\')".
                    format(title, body, author))
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
# @is_logged_in
def user_list():
    cur = con.cursor()
    result = cur.execute('select * from users')
    users = cur.fetchall()
    directory = os.path.join(APP_ROOT, 'images')
    image_path = os.path.join(directory, 'cat.jpg')
    print(image_path)
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
    choices=[('bloodgroup','bloodgroup')]
    select=SelectField('Search For Blood', choices=choices)
    search=StringField('')


#Search Items
@app.route('/search', methods=['GET', 'POST'])
#create_cursor
def search():
    search=SearchForm(request.form)
    if request.method=='POST':
        print(request.data)
        return search_results(search)
    return render_template('search.html', form=search)


@app.route('/results')
def search_results(search):
    search_string = search.data['search']
    if search_string:
        if search.data['select'] == 'bloodgroup':
            cur =con.cursor()
        cur.execute('''select * from users where bloodgroup=:bloodgroup''', bloodgroup=search_string)
        results =cur.fetchall()
        print(results)
        from pprint import pprint
        pprint(results)
        print(len(results))

    if not results:
        flash('No results found!ha ha ha')
        return redirect('search.html')
    else:
        return render_template('results.html', results=results)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
