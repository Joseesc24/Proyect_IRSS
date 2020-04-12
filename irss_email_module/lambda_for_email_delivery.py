# --------------------------------------------------------------------------------------------
# Antes de poder envir correos en Gmail es importante habilitar el acceso a aplicaciones poco
# seguras en: https://www.google.com/settings/security/lesssecureapps
# esta funcion lambda trabaja sobre el bucket: irss.processed.images.bucket
# --------------------------------------------------------------------------------------------
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import os, boto3, smtplib


def lambda_handler(event, context):
    image_name = str(event['Records'][0]['s3']['object']['key'])
    bucket_name = str(event['Records'][0]['s3']['bucket']['name'])
    download_image_from_s3_to_temp(image_name, bucket_name)
    send_email('josedanielescobarmurci@gmail.com', image_name)
    remove_image_from_lambda_temp(image_name)


def download_image_from_s3_to_temp(image_name, bucket_name):
    boto3.client('s3').download_fileobj(bucket_name, image_name, open('/tmp/' + image_name, 'wb'))


def load_image_from_lambda_temp(image_name):
    return open('/tmp/' + image_name, 'rb')


def remove_image_from_lambda_temp(image_name):
    if os.path.exists('/tmp/' + image_name):
        os.remove('/tmp/' + image_name)


def create_email(user_emial, irss_email, image_name):
    subject = 'Results of remasterize the image ' + str(image_name) + ' with IRSS'
    body_text = 'Hi dear user, here you have your image remasterized.'
    image = load_image_from_lambda_temp(image_name).read()
    part = MIMEApplication(image, Name=image_name)
    part['Content-Disposition'] = 'attachment; filename="%s"' % image_name
    email = MIMEMultipart()
    email['Date'] = formatdate(localtime=True)
    email['Subject'] = subject
    email['From'] = irss_email
    email['To'] = user_emial
    email.attach(MIMEText(body_text))
    email.attach(part)
    email = email.as_string()
    return email


def send_email(user_emial, image_name):
    irss_email = 'irss.results@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(irss_email, 'holamundo')
    server.sendmail(
        irss_email, user_emial, create_email(
            user_emial,
            irss_email,
            image_name
        ))
    server.close()
