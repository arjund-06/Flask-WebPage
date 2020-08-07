from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)['params']

app = Flask(__name__)
app.secret_key='super-secret-key'
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = "465",
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-username'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
db = SQLAlchemy(app)


class contacts(db.Model):
    sno =db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(50), nullable=False)
    email =db.Column(db.String(50), nullable=False)
    phone =db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(50), nullable=False)
    date =db.Column(db.String(13), nullable=False)

class posts(db.Model):
    sno =db.Column(db.Integer, primary_key=True)
    title =db.Column(db.String(50), nullable=False)
    post_slug =db.Column(db.String(50), nullable=False)
    content =db.Column(db.String(20), nullable=False)
    img_file =db.Column(db.String(25), nullable=False)
    date =db.Column(db.String(13), nullable=False)

@app.route('/')
def index():
    Posts= posts.query.filter_by().all()
    return render_template("index.html", params=params, Posts=Posts)

@app.route('/login', methods=['POST','GET'])
def login():
    if 'user' in session and session['user'] == params['admin-username']:
        return redirect("/admin")
    else:
        if request.method =="POST":
            username = request.form.get('username')
            password = request.form.get('password')
            if username == params['admin-username'] and password == params['admin-password']:
                session['user'] = username
                return redirect("/admin")

    return render_template("login.html")

@app.route('/admin')
def admin():
    if 'user' in session and session['user'] == params['admin-username']:
        Posts= posts.query.filter_by().all()
        return render_template("admin.html", params=params, Posts=Posts)
    else:
        return render_template("login.html")

@app.route('/edit/<string:sno>', methods=['POST','GET'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin-username']:
        if request.method == 'POST':
            title = request.form.get('title')
            post_slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get("img_file")
            
            post= posts.query.filter_by(sno = sno).first()
            post.title = title
            post.post_slug = post_slug
            post.content =  content
            db.session.commit()
            return redirect("/admin")
        Post = posts.query.filter_by(sno = sno).first()
        return render_template("edit.html", params=params, Post = Post)

@app.route('/delete/<string:sno>', methods=['GET'])
def delete(sno):
    post = posts.query.filter_by(sno = sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/admin")

@app.route('/add', methods=['POST','GET'])
def add():
    if 'user' in session and session['user'] == params['admin-username']:
        if request.method == 'POST':
            title = request.form.get('title')
            post_slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get("img_file")

            post= posts(title= title, post_slug= post_slug, content= content, img_file= img_file, date=datetime.now())
            db.session.add(post)
            db.session.commit()
            return redirect("/admin")
        return render_template("add.html", params=params)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/post/<string:slug>', methods=['GET'])
def post_route(slug):
    post = posts.query.filter_by(post_slug = slug).first()
    return render_template("post.html", params=params, post=post)

@app.route('/contact', methods = ['POST','GET'])
def contact():
    if(request.method=='POST'):
        name= request.form.get('name')
        email= request.form.get('email')
        phone= request.form.get('phone')
        msg= request.form.get('msg')
        data = contacts(name=name, email=email, phone=phone, msg=msg, date=datetime.now())
        db.session.add(data)
        db.session.commit()
        mail.send_message('New message from blog website',
                        sender = params["gmail-username"],
                        recipients = [params["gmail-username"]],
                        body = msg + "\n Phone number is" + phone + "\n EMAIL " + email 
                        )
        # themail.body=msg + "\n" + msg
        # mail.send(themail)
    return render_template("contact.html", params=params)

app.run(debug=True)

