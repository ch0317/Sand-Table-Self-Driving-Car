
import cv2
import numpy as np
import socket
from model import NeuralNetwork
import urllib.request

HOST = "192.168.11.1:8080"

class sock_car_control(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        conn = self.sock.connect(("192.168.11.1", 2001))
        if conn:
            print ("socket connect.")

    def steer(self, prediction):
        if prediction == 2:
            self.sock.send(chr(1).encode())
            print("Forward")
        elif prediction == 0:
            self.sock.send(chr(7).encode())
            print("Left")
        elif prediction == 1:
            self.sock.send(chr(6).encode())
            print("Right")
        else:
            self.stop()

    def stop(self):
        self.serial_port.write(chr(0).encode())


class RCDriverNNOnly(object):

    def __init__(self, host, port, serial_port, model_path):

        # load trained neural network
        self.nn = NeuralNetwork()
        self.nn.load_model(model_path)

        self.car_ctrl = sock_car_control()

    def drive(self):
        stream_bytes = b' '
        stream = urllib.request.urlopen(host_str)
        try:
            # stream video frames one by one
            while True:
                stream_bytes += stream.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    gray = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    # lower half of the image
                    height, width = gray.shape
                    roi = gray[int(height/2):height, :]

                    cv2.imshow('image', image)
                    # cv2.imshow('mlp_image', roi)

                    # reshape image
                    image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)

                    # neural network makes prediction
                    prediction = self.nn.predict(image_array)
                    self.rc_car.steer(prediction)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("car stopped")
                        self.rc_car.stop()
                        break
        finally:
            cv2.destroyAllWindows()
            self.sock.close()


if __name__ == '__main__':
    # host_str
    host_str = 'http://' + HOST + '/?action=stream'
    print ('Streaming ' + host_str)

    # model path
    path = "saved_model/nn_model.xml"

    rc = RCDriverNNOnly(host_str, path)
    rc.drive()
