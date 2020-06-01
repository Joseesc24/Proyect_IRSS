# --------------------------------------------------------------------------------------------
# Antes de poder envir correos en Gmail es importante habilitar el acceso a aplicaciones poco
# seguras en: https://www.google.com/settings/security/lesssecureapps
# esta funcion lambda trabaja sobre el bucket: irss.processed.images.bucket
# en las politicas de lambda es necesario aumentar el tiempo de ejecucion a minimo 10 segundos
# y autorizar el acceso a s3 y dynamodb.
# --------------------------------------------------------------------------------------------
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import os, boto3, smtplib


def lambda_handler(event, context):
    image_hash = str(event['Records'][0]['s3']['object']['key'])
    bucket_name = str(event['Records'][0]['s3']['bucket']['name'])
    download_image_from_s3_to_lambda_temp(image_hash, bucket_name)
    image_meta_data = get_item_dynamodb(image_hash.split(".")[0])
    send_email(image_meta_data, image_hash)
    remove_image_from_lambda_temp(image_hash)


def download_image_from_s3_to_lambda_temp(image_hash, bucket_name):
    boto3.client('s3').download_fileobj(bucket_name, image_hash, open('/tmp/' + image_hash, 'wb'))


def load_image_from_lambda_temp(image_hash):
    return open('/tmp/' + image_hash, 'rb')


def remove_image_from_lambda_temp(image_hash):
    if os.path.exists('/tmp/' + image_hash):
        os.remove('/tmp/' + image_hash)


def create_email(user_emial, irss_email, image_hash, image_name):
    image_extension = image_hash.split(".")[-1]
    subject = 'Results of remasterize the image ' + str(image_name) + ' with IRSS'
    image_name = image_name + "." + image_extension
    body_text = 'Hi dear user here you have your image remasterized, please save it carefully, before sending this mail your image was erased from our servers, so if you lose it you are going to need to restart the proces for geting it again.'
    image = load_image_from_lambda_temp(image_hash).read()
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


def send_email(image_meta_data, image_hash):
    user_email = image_meta_data['user_email']
    image_name = image_meta_data['image_original_name']
    irss_email = 'irss.results@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(irss_email, 'holamundo')
    server.sendmail(
        irss_email, user_email, create_email(
            user_email,
            irss_email,
            image_hash,
            image_name
        )
    )
    server.close()


def get_item_dynamodb(image_hash):
    import boto3
    flow_control_table = boto3.resource('dynamodb').Table('irss_flow_control_table')
    if check_if_item_exist_dynamo(image_hash) is True:
        item = flow_control_table.get_item(
            Key={
                'image_hash': str(image_hash)
            }
        )
        item = item['Item']
        return item
    elif check_if_item_exist_dynamo(image_hash) is False:
        return None


def check_if_item_exist_dynamo(image_hash):
    import boto3
    flow_control_table = boto3.resource('dynamodb').Table('irss_flow_control_table')
    item = flow_control_table.get_item(
        Key={
            'image_hash': str(image_hash)
        }
    )
    if 'Item' in [key for key in item]:
        return True
    else:
        return False
