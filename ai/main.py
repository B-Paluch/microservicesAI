import json
import re
import os

import requests
from kafka import KafkaConsumer, KafkaProducer
from network.detect import doNetwork

producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_HOST', "localhost:9092"),
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))  # os.environ['KAFKA_BOOTSTRAP']
consumer = KafkaConsumer('fileCreated', group_id='ai', bootstrap_servers=os.getenv('KAFKA_HOST', "localhost:9092"),
                         auto_offset_reset='earliest')


def getFilename_fromCd(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


print('server is running script.')

for msg in consumer:
    try:
        r = requests.get(os.getenv('UPLOADER', "http://localhost:8999") + "/files/" + msg.value.decode("utf-8"))
        filename = getFilename_fromCd(r.headers.get('content-disposition')).strip('"')
        print(filename)
        if filename.endswith(('.jpg', '.jpeg')):
            file = open(filename, 'wb')
            file.write(r.content)
            file.close()
            doNetwork(filename)
            image = open("result"+filename,'rb')
            payload = {'name': filename}
            i = requests.post(os.getenv('BLOG', "http://localhost:8001")+"/api/images/", data=payload, files={'photo':image})
            print(payload)
            print(i.content)
            image.close()
            # requests.post("http://localhost:8001/api/images/", data=payload, files = file)

            file.close()
            message = {
                "service": "ai",
                "value": "processing succeded."
            }
            producer.send('processingSucceded', {
                "service": "ai",
                "value": "processing succeded."})
        else:
            print('failed')
            producer.send('processingFailed', {
                "service": "ai",
                "value": "processing failed due to not proper extension of file. File needs to be an image in jpg format."
            })
    except Exception as e:
        print("failed :(")
        producer.send('processingFailed', {
            "service": "ai",
            "value": "Source server or destination server is unavailable."
        })
