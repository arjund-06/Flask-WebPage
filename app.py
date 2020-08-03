from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

local_server = True

with open('config.json', 'r') as c:
    params = json.load(c)['params']

app = Flask(__name__)
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

