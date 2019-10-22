import numpy as np
import cv2
import pygame
from pygame.locals import *
import socket
from time import sleep
import os
import urllib.request
import serial
import serial.tools.list_ports
import json
import _thread

HOST = "192.168.11.1:8080"


class CarDrive(object):
    
    def __init__(self, host_str):

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        conn = self.sock.connect(("192.168.11.1", 2001))
        if conn:
            print ("socket connect.")

        self.send_inst = True

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1

        pygame.init()
        pygame.display.set_mode((250, 250))


    def key_drive(self):

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print("Start collecting images...")
        print("Press 'q' or 'x' to finish...")
        start = cv2.getTickCount()

        stream = urllib.request.urlopen(host_str)

        # stream video frames one by one
        try:
            stream_bytes = b' '
            frame = 1
            while self.send_inst:
                stream_bytes += stream.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    # change picture to grey
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    #image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8))
                    
                    # select lower half of the image, region of interesting
                    height, width = image.shape
                    roi = image[int(height/2):height, :]

                    cv2.imshow('image', image)

                    # reshape the roi image into a vector
                    temp_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
                    
                    frame += 1
                    total_frame += 1

                    # get input from human driver
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            key_input = pygame.key.get_pressed()

                            # complex orders
                            if key_input[pygame.K_UP] and key_input[pygame.K_RIGHT]:
                                print("Forward Right")
                                self.sock.send(chr(6).encode())

                            elif key_input[pygame.K_UP] and key_input[pygame.K_LEFT]:
                                print("Forward Left")
                                self.sock.send(chr(7).encode())

                            elif key_input[pygame.K_DOWN] and key_input[pygame.K_RIGHT]:
                                print("Reverse Right")
                                self.sock.send(chr(8).encode())

                            elif key_input[pygame.K_DOWN] and key_input[pygame.K_LEFT]:
                                print("Reverse Left")
                                self.sock.send(chr(9).encode())

                            # simple orders
                            elif key_input[pygame.K_UP]:
                                print("Forward")
                                self.sock.send(chr(1).encode())

                            elif key_input[pygame.K_DOWN]:
                                print("Reverse")
                                self.sock.send(chr(2).encode())

                            elif key_input[pygame.K_RIGHT]:
                                print("Right")
                                self.sock.send(chr(3).encode())

                            elif key_input[pygame.K_LEFT]:
                                print("Left")
                                self.sock.send(chr(4).encode())

                            elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                                print("exit")
                                self.send_inst = False
                                self.sock.send(chr(0).encode())
                                self.sock.close()
                                break

                        elif event.type == pygame.KEYUP:
                            self.sock.send(chr(0).encode())

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break


            end = cv2.getTickCount()
        finally:
            self.sock.close()

    def forward(self):
        print("Forward")
        self.sock.send(chr(1).encode())

    def backward(self):
        print("Reverse")
        self.sock.send(chr(2).encode())

    def left(self):
        print("Right")
        self.sock.send(chr(3).encode())

    def right(self):
        print("Left")
        self.sock.send(chr(4).encode())

    def stop(self):
        print("stop")
        self.sock.send(chr(0).encode())

class Ser(object):

    def __init__(self):
        pass

    def Serial_connect(self):
        plist = list(serial.tools.list_ports.comports())
        serialName = []
        if len(plist) < 1:
            print ("The Serial port can't find!")
        else:
            for com_port in plist:
                if(com_port[0] != 'COM1'):
                    serialName = com_port[0]
            try:
                self.S = serial.Serial(serialName,115200,timeout = 0.5)
                print("Serial Port %s success" % serialName)
            except:
                print("Serial Port Fail.")

    def recv(self):
        line = []
        data = ''
        while True:

            cc = self.S.readline().decode()
            #print(cc)
            if len(cc) == 0:
                break
            data += cc

        if data:
            text = json.loads(data)
            return text
        else:
            print("DATA NONE")
    def check(self):
        self.S.write('s'.encode())




def ser_fun(SER,cardrive):

    cardrive.forward()
    while True:
        j = SER.recv()
        if j != None:
            print(j)
            if(j['state'] == 'open'):
                cardrive.stop()
                break
    sleep(2)
    cardrive.forward()
    sleep(3)
    cardrive.stop()



def serial_check(SER):
    while True:
        sleep(5)
        try:
            SER.check()
        except:
            print("reconnect")
            SER.Serial_connect()




if __name__ == '__main__':

    host_str = 'http://' + HOST + '/?action=stream'
    print ('Streaming ' + host_str)
    cardrive = CarDrive(host_str)
    SER = Ser()
    SER.Serial_connect()
    # vector size, half of the image
    s = 120 * 320
    _thread.start_new_thread( ser_fun, (SER,cardrive,) )
    _thread.start_new_thread( serial_check, (SER,) )
    cardrive.key_drive()


