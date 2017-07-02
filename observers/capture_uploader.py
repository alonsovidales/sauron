import boto3
import sys

class CaptureUploader(object):
    def __init__(self, aws_connection, bucket_name, region):
        self._s3 = boto3.client('s3', region)
        self._bucket = bucket_name

    def detection(self, img_data, diff):
        img_data['name'] = img_data['path'].split('/')[-1]
        self._s3.upload_file(img_data['path'], self._bucket, img_data['name'])
