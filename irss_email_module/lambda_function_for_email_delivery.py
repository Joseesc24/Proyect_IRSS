# --------------------------------------------------------------------------------------------
# Antes de poder envir correos en Gmail es importante habilitar el acceso a aplicaciones poco
# seguras en: https://www.google.com/settings/security/lesssecureapps
# --------------------------------------------------------------------------------------------
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import json, boto3, smtplib


def lambda_handler(event, context):
    nombre_archivo = str(event['Records'][0]['s3']['object']['key'])
    nombre_bucket = str(event['Records'][0]['s3']['bucket']['name'])
    lambda_download_file_from_s3(nombre_archivo, nombre_bucket)
    return {
        'statusCode': 200,
        'body': json.dumps('Archivo enviado.')
    }


def lambda_download_file_from_s3(original_file, bucket):
    boto3.client('s3').download_fileobj(bucket, original_file, open('/tmp/' + original_file, 'wb'))


def create_email(user_emial, irss_email, image_name):
    subject = 'Resultado reescalado de la imagen ' + str(image_name) + 'con IRSS'
    body_text = 'Hola querido usuario, adjuntamos en este correo el resultado de reescalar la imagen ' + \
                str(image_name) + ' con IRSS.'
    image = open(image_name, 'rb').read()
    part = MIMEApplication(image, Name=image_name)
    part['Content-Disposition'] = 'attachment; filename="%s"' % image_name
    email = MIMEMultipart()
    email['Date'] = formatdate(localtime=True)
    email['Subject'] = subject
    email['From'] = irss_email
    email['To'] = user_emial
    email.attach(MIMEText(body_text))
    email.attach(part)
    return email.as_string()


def send_email(user_emial, image_name):
    irss_email = 'irss.results@gmail.com'
    irss_password = 'holamundo'
    server = smtplib.SMTP('smtp.gmail.com: 587')
    try:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(irss_email, irss_password)
        server.sendmail(
            irss_email,
            user_emial,
            create_email(user_emial, irss_email, image_name)
        )
        server.close()
        return True
    except:
        server.close()
        return False


send_email('josedanielescobarmurci@gmail.com', 'Ar8.jpg')
