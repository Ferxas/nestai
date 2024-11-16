from flask import Flask, request, jsonify, render_template, url_for
from pymongo import MongoClient
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configuración del servidor (necesario para generar URLs absolutas)
app.config['SERVER_NAME'] = '127.0.0.1:5000'

# MongoDB configuración
client = MongoClient('mongodb://localhost:27017/')
db = client['donation_db']
users_collection = db['users']

# Configuración Flask-Mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_USERNAME')
)

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    data['start_donate_date'] = datetime.now()
    users_collection.insert_one(data)
    
    # Enviar correo de bienvenida
    send_mail(
        to=data['email'],
        subject='¡Bienvenido/a a NestAi! 🎉',
        template_name='welcome_email.html',
        donor_name=data.get('name', 'Amigo/a'),
        image_path=os.path.join('static', 'img', 'welcome_email.webp'),
        calendar_url=url_for('static', filename='img/calendar.webp', _external=True),
        logo_url=url_for('static', filename='img/logo.png', _external=True)
    )
    return jsonify({'message': 'Usuario registrado correctamente.'}), 201

def send_mail(to, subject, template_name, **kwargs):
    """
    Enviar correos electrónicos usando plantillas HTML con imágenes embebidas y URLs públicas.
    """
    # Renderizar contenido HTML del correo
    html_content = render_template(template_name, **kwargs)
    msg = Message(subject, recipients=[to])
    msg.html = html_content

    # Adjuntar logo como imagen embebida
    with app.open_resource(os.path.join('static', 'img', 'logo.png')) as logo:
        msg.attach(
            'logo.png', 
            'image/png', 
            logo.read(), 
            'inline', 
            headers={'Content-ID': '<logo>'}
        )

    # Adjuntar imagen principal como imagen embebida
    if 'image_path' in kwargs:
        with app.open_resource(kwargs['image_path']) as main_image:
            msg.attach(
                os.path.basename(kwargs['image_path']),
                'image/webp',
                main_image.read(),
                'inline',
                headers={'Content-ID': '<main_image>'}
            )

    mail.send(msg)

# Tarea para verificar aniversarios
def chek_users_for_anniversaries():
    today = datetime.now()
    for user in users_collection.find():
        if user['start_donate_date'] + timedelta(days=365) <= today:
            send_mail(
                to=user['email'],
                subject='¡Feliz aniversario con NestAi! 🎉',
                template_name='anniversary_email.html',
                donor_name=user.get('name', 'Amigo/a'),
                image_path=os.path.join('static', 'img', 'poverty.webp'),
                logo_url=url_for('static', filename='img/logo.png', _external=True),
                talkual_link='https://www.talkualfoods.com/',
                nestai_link='https://www.nestai.com'
            )

# Tarea para verificar inactividad de donaciones
def check_users_for_inactivity():
    today = datetime.now()
    for user in users_collection.find():
        last_donation_date = user.get('last_donate_date')
        if last_donation_date and isinstance(last_donation_date, datetime):
            if last_donation_date + timedelta(days=30) <= today:
                send_mail(
                    to=user['email'],
                    subject='Te extrañamos en NestAi 💔',
                    template_name='story_email.html',
                    donor_name=user.get('name', 'Amigo/a'),
                    image_path=os.path.join('static', 'img', 'story_email.webp'),
                    logo_url=url_for('static', filename='img/logo.png', _external=True),
                    video_url=url_for('static', filename='videos/aminata.mp4', _external=True)
                )

# Configuración de tareas automáticas
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=chek_users_for_anniversaries, trigger='interval', days=1)
scheduler.add_job(func=check_users_for_inactivity, trigger='interval', days=1)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
