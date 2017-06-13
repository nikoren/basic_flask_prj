from flask_mail import Message
from flask import current_app, render_template
from threading import Thread
from . import mail, celery


def send_async_email(msg, app):
    '''
    This function is built so it can me run from separate thread,
    this is why current_app context should be saved

    Parameters:
    ------------
        msg: The msg with all the data pre-populated

    '''

    with app.app_context():
        mail.send(msg)

@celery.task
def send_async_celery_email(msg):
    mail.send(msg)

def send_email(to_email_address, subject, template, **kwargs):
    '''
    Constructs the message and sends it asynchronously

    :param user: User
        user to send to
    :param subject: String
        Email subject
    :param template: String
        os.path to template of email content,
        this function assumes two templates versions with this name exist
        the files should have following extensions (txt/html)

    :param kwargs:
        additional kwargs that can be used in templates, e.g token

    :return: Thread instance
        Instance of thread that include all the information regarding messange sending process
    '''

    # Construct the message
    msg = Message(
        current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
        sender=current_app.config['MAIL_SENDER'], recipients=[to_email_address])
    msg.body = render_template(template + '.txt', **kwargs)  # for email kwargs expected to have token and user objects
    msg.html = render_template(template + '.html', **kwargs) # for email kwargs expected to have token and user objects

    if kwargs.get('use_thread'):
        # Send the message via thread
        app = current_app._get_current_object()

        email_thread = Thread(target=send_async_email, args=[msg, app])
        email_thread.start()

    if kwargs.get('use_celery'):
        send_async_celery_email.delay(msg)


