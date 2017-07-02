import boto
import time

from capturer.camera_capture import CameraCapture
from observers.capture_analyzer import CaptureAnalyzer
from observers.capture_uploader import CaptureUploader

class Observer(object):
    def detection(self, img_file, diff):
        print("Something was detected!!! %s %d" % (img_file, diff))

S3_BUCKET = 'sauron-alarm'
AWS_REGION = 'us-east-1'

conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                       AWS_SECRET_ACCESS_KEY)

cc = CameraCapture()

# Test observer
cc.add_observer(Observer())

cc.add_observer(CaptureUploader(conn, S3_BUCKET, AWS_REGION))
cc.add_observer(CaptureAnalyzer(conn, S3_BUCKET, AWS_REGION, False))

cc.start_capturing()
time.sleep(10)
