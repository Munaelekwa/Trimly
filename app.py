from flask import Flask, render_template, url_for, flash, redirect, request, send_file
import os
import validators
import shortuuid
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from utils import db, generate_qr_code
from models import User, Link, Qrcode
from forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm , NewLinkForm, NewQrcodeForm
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_login import LoginManager, login_user, logout_user, current_user

base_dir = os.path.dirname(os.path.realpath(__file__))
load_dotenv()
app = Flask(__name__)

#app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300


db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)
bcrypt = Bcrypt(app)
cache = Cache(app)
mail = Mail(app)
limiter = Limiter(app)
login_manager  = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/links")
def links():
    links = Link.query.filter_by(user_id=current_user.id).order_by(Link.created_at.desc()).all()
    host = request.host_url
    return render_template('links.html', host=host, links=links)


@app.route("/qrcodes")
def qrcodes():
    qrcodes = Qrcode.query.filter_by(user_id=current_user.id).order_by(Qrcode.created_at.desc()).all()
    host = request.host_url
    return render_template('qrcodes.html', qrcodes=qrcodes, host=host)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_pword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_pword)
        user.save()
        flash('Account has been created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='SignUp', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            return render_template('dashboard.html')
        else:
            flash('Login Unsuccessful, please check that email and password are correct.', 'error')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
	return render_template("dashboard.html")

@app.route('/new-link', methods=['GET', 'POST'])
def new_link():
    form = NewLinkForm()
    if form.validate_on_submit():
    	if validators.url(form.long_url.data):
            custom_url = form.custom_url.data or None
            if custom_url:
                url = Link.query.filter_by(custom_url=custom_url).first()
                if url:
                    flash('That custom url already exists! please try another one!')
                    return redirect(url_for('new_link'))
                short_url = custom_url
            else:
                short_url = shortuuid.ShortUUID().random(6)
            link = Link(title=form.title.data or None, original_url=form.long_url.data, custom_url=custom_url, shortened_url=short_url, user_id=current_user.id)
            link.save()
            flash('Link Created Succesfully', 'success')
            return redirect(url_for('links'))

    return render_template('createlink.html', form=form)

@app.route('/link<int:id>/edit', methods=['GET', 'POST'])
def edit_link(id):
    link = Link.query.get_or_404(id)
    form = NewLinkForm()
    if form.validate_on_submit():
        link.title = form.title.data
        link.custom_url = form.custom_url.data
        link.original_url = form.long_url.data
        db.session.commit()
        flash('Link has been updated Successfully.', 'success')
        return redirect(url_for('details', id=id))
    form.title.data = link.title
    form.custom_url.data = link.custom_url
    form.long_url.data = link.original_url
    form.long_url.render_kw = {'readonly': 'readonly'}
    return render_template('createlink.html', link=link, form=form)

@app.route('/link<int:id>/delete', methods=['POST', 'GET'])
def del_link(id):
    link = Link.query.get_or_404(id)
    link.delete()
    flash('Link deleted.',  'success')
    return redirect(url_for('links'))

@app.route('/new_qrcode', methods=['GET', 'POST'])
def new_qrcode():
    form = NewQrcodeForm()
    if form.validate_on_submit():
        if validators.url(form.url.data):
            code = shortuuid.ShortUUID().random(8)
            qrcode = Qrcode(url=form.url.data, code=code, title=form.title.data or None, user_id=current_user.id)
            qrcode.save()
            flash('Qrcode generated successfully', 'success')
            return redirect(url_for('qrcodes'))
        return 'Invalid Url!'
    return render_template('createqr.html', form=form)

@app.route('/link<int:id>/details')
def details(id):
    link = Link.query.filter_by(id=id).first()
    host = request.host_url
    if link:
        return render_template('details.html', link=link, host=host)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email.lower()).first()
        link = request.host_url + "reset_password/" + email
        if user:
            try:
                msg = Message('Reset Password', sender="Trimly", recipients=[email])
                msg.body = f"Hello {user.username},\nwe received a request to reset your password \nfollow the link below to change your password: \n{link}\nYou can ignore this mail if you didn't make the request."
                mail.send(msg)
            except:
                flash ("Reset password failed. Please try again.")
                return redirect(url_for('login'))
            flash('Reset password link sent successfully. Please check your mail inbox or spam.')
            return redirect(url_for('login'))
        flash('Email not reistered. please signup to register.')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html', form=form)

@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    form = ResetPasswordForm()
    user = User.query.filter_by(email=email.lower()).first()
    if form.validate_on_submit():
        hashed_pword = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        user.password = hashed_pword
        db.session.commit()
        flash('Password reset successfully. Please login.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/<short_url>')
@limiter.limit('10/minute')
@cache.cached(timeout=60)
def redirect_url(short_url):
    link = Link.query.filter_by(shortened_url=short_url).first()
    qr = Qrcode.query.filter_by(code=short_url).first()
    if link:
        link.clicks += 1
        db.session.commit()
        return redirect(link.original_url)
    elif qr:
        qr.scans += 1
        db.session.commit()
        return redirect(qr.url)
    else:
        return 'Url not Found!'


@app.route('/qrcode<int:id>/download')
@cache.cached(timeout=60)
def download_qrcode(id):
    qrcode = Qrcode.query.filter_by(id=id).first()
    if qrcode:
        url = request.host_url + qrcode.code
        file = generate_qr_code(url)
        response = send_file(file, mimetype='image/png', as_attachment=True, download_name='qrcode.png')
        return response


