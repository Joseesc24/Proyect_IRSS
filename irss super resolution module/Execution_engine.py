from Run_ESRGAN import Run as run_esrgan
import os, time, boto3

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='irss_not_processed_images_queue.fifo')

download_bucket = "irss.not.processed.images.bucket"
upload_bucket = "irss.processed.images.bucket"


def check_if_item_exist_dynamo(image_hash):
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


def get_item_dynamodb(image_hash):
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


def download_image_from_s3(image_name, bucket_name):
    boto3.client('s3').download_fileobj(bucket_name, image_name, open('./LR/' + image_name, 'wb'))


def lambda_upload_file_to_s3(image_name, bucket_name, new_image_name):
    boto3.client('s3').upload_fileobj(open('./HR/' + image_name, 'rb'), bucket_name, new_image_name)


def delete_file_from_s3(filename, bucket_name):
    boto3.client('s3').delete_object(Bucket=bucket_name, Key=filename)


while True:

    try:

        message = queue.receive_messages(MessageAttributeNames=['All'])[0]
        print("")

        queue.delete_messages(
            Entries=[
                {
                    'Id': str(message.message_id),
                    'ReceiptHandle': str(message.receipt_handle)
                },
            ]
        )

        nombre_imagen = str(message.message_attributes['image_name']['StringValue'])
        hash_imagen = str(message.message_attributes['image_hash']['StringValue'])
        print("Nombre de la siguiente imagen: " + str(nombre_imagen))
        print("Hash de la siguiente imagen: " + hash_imagen)
        download_image_from_s3(nombre_imagen, download_bucket)
        print("Imagen descargada")
        run_esrgan()
        print("Imagen reescalada")
        if os.path.exists('./LR/' + nombre_imagen):
            os.remove('./LR/' + nombre_imagen)
            print("Imagen original borrada del almacenamiento local")
        nombre_imagen, extension = nombre_imagen.split(".")
        nombre_imagen = nombre_imagen + "_rlt.png"
        print("Nombre de la imagen reescalada: " + nombre_imagen)
        time.sleep(20)
        new_image_name = hash_imagen + ".png"
        lambda_upload_file_to_s3(nombre_imagen, upload_bucket, new_image_name)
        print("Imagen reescalda subida a s3")
        if os.path.exists('./HR/' + nombre_imagen):
            os.remove('./HR/' + nombre_imagen)
            print("Imagen reescalada borrada del almacenamiento local")
        delete_file_from_s3(nombre_imagen, download_bucket)
        print("Imagen original borrada de s3")
        print("Imagen " + nombre_imagen + " escalada y entrgada en " + upload_bucket)

        time.sleep(60)

    except:
        time.sleep(60)
