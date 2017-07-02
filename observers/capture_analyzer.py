import boto3
import sys
from boto.s3.key import Key

from botocore.exceptions import ClientError

class CaptureAnalyzer(object):
    _people_labels = set(('Human', 'Person', 'People'))

    def __init__(self, aws_connection, bucket_name, region, faces_acquisition):
        self._bucket = bucket_name
        self._client = boto3.client('rekognition', region)
        self._faces_acquisition = faces_acquisition

    def detection(self, img_data, diff):
        if self._faces_acquisition:
            try:
                # We are going to use the same name for the collection as for the
                # bucket
                collection_create = self._client.create_collection(
                    CollectionId=self._bucket
                )
                print("Collection create:", collection_create)
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                    print("Collection alrady created")
                else:
                    raise e

            response_index = self._client.index_faces(
                CollectionId=self._bucket,
                Image={
                    'S3Object': {
                        'Bucket': self._bucket,
                        'Name': img_data['name']
                    }
                },
                DetectionAttributes=[
                    'ALL'
                ]
            )

            for face in response_index['FaceRecords']:
                print("Face:", face['Face']['FaceId'], response_index['FaceRecords'][0]['FaceDetail'])
        else:
            response = self._client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': self._bucket,
                        'Name': img_data['name'],
                    },
                },
                MaxLabels=20,
                MinConfidence=70,
            )

            img_data['labels'] = set([l['Name'] for l in response['Labels']])
            print("Analyze:", self._bucket, img_data)
            if len(CaptureAnalyzer._people_labels & img_data['labels']) > 0:
                print "DETECTION!!!!!!:", len(CaptureAnalyzer._people_labels & img_data['labels']), CaptureAnalyzer._people_labels & img_data['labels']
                search_result = self._client.search_faces_by_image(
                    CollectionId=self._bucket,
                    Image={
                        'S3Object': {
                            'Bucket': self._bucket,
                            'Name': img_data['name']
                        }
                    },
                    MaxFaces=5,
                    FaceMatchThreshold=90
                )
                print "Search Result:", search_result
