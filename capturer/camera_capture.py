import datetime
import picamera
import StringIO
import threading
import time
import os

from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average

class CameraCapture(object):
    def __init__(self, diff_ratio=2, quality=100, interval_sec=1, tmp_dir='/tmp'):
        self._camera = picamera.PiCamera()
        self._observers = []
        self._interval = interval_sec
        self._diff_ratio = diff_ratio
        self._quality = quality
        self._tmp_dir = tmp_dir

    def add_observer(self, observer):
        self._observers.append(observer)

    def start_capturing(self):
        #threading.Thread(target=self._start_capturing).start()
        self._start_capturing()

    def _compare_images(self, img1, img2):
        # normalize to compensate for exposure difference
        img1 = self._normalize(img1)
        img2 = self._normalize(img2)
        # calculate the difference and its norms
        diff = img1 - img2  # elementwise for scipy arrays
        m_norm = sum(abs(diff))  # Manhattan norm

        return m_norm

    def _to_grayscale(self, arr):
        # If arr is a color image (3D array), convert it to grayscale (2D array).
        if len(arr.shape) == 3:
            return average(arr, -1)  # average over the last axis (color channels)
        else:
            return arr

    def _normalize(self, arr):
        rng = arr.max()-arr.min()
        amin = arr.min()
        return (arr-amin)*255/rng

    def _start_capturing(self):
        prev_content = None
        while True:
            print("Capturing!!!")
            file_name = '{}/{}.jpg'.format(self._tmp_dir, datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
            self._camera.capture(file_name, format='jpeg', quality=self._quality)
            content = self._to_grayscale(imread(file_name).astype(float))
            distance = 0.0
            if prev_content is not None:
                n_m = self._compare_images(content, prev_content)
                diff = n_m/prev_content.size
                if diff > self._diff_ratio:
                    print "Detection by Manhattan norm:", n_m, "/ per pixel:", n_m/prev_content.size

                    file_data = {
                        'path': file_name
                    }
                    for obs in self._observers:
                        obs.detection(file_data, diff)

                os.unlink(prev_path)

            prev_content = content
            prev_path = file_name
            print("Captured:", len(content), distance/len(content))
            time.sleep(self._interval)

if __name__ == '__main__':
    class Observer(object):
        def detection(self, img_file, diff):
            print("Something was detected!!! %s %d" % (img_file, diff))

    cc = CameraCapture()
    cc.add_observer(Observer())
    cc.start_capturing()
    time.sleep(10)
