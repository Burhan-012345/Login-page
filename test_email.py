from flask import Flask
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

@app.route('/test')
def test_email():
    try:
        msg = Message(
            subject='Test Email from Flask',
            recipients=['ahmedburhan4834@gmail.com'],
            body='This is a test email from your Flask application.'
        )
        mail.send(msg)
        return 'Test email sent successfully!'
    except Exception as e:
        return f'Error sending email: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
