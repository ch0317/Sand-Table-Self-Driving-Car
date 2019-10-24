import numpy as np
import cv2
import pygame
from pygame.locals import *
import socket
from time import sleep
import os
import urllib.request
import requests
import serial
import serial.tools.list_ports
import json
import _thread
import re

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
        self.screen = pygame.display.set_mode((420, 240))
        pygame.display.set_caption('智能网联无人车')
        self.background_image = pygame.image.load("background.jpg").convert()
        self.forward_image = pygame.image.load("forward.png").convert()
        self.backward_image = pygame.image.load("backward.png").convert()
        self.left_image = pygame.image.load("left.png").convert()
        self.right_image = pygame.image.load("right.png").convert()
        self.stop_image = pygame.image.load("stop.png").convert()

    def key_drive(self):
        try:
            # collect images for training
            print("Start collecting images...")
            start = cv2.getTickCount()

            stream = urllib.request.urlopen(host_str)
        except:
            print("connect fail.")

        try:
            stream_bytes = b''
            while self.send_inst:
                stream_bytes += stream.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    # change picture to grey
                    #image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    self.screen.fill([0, 0, 0])
                    #image = cv2.cvtColor(jpg, cv2.COLOR_BGR2RGB)
                    image = np.rot90(image)
                    # image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8))
                    image = pygame.surfarray.make_surface(image)
                    self.screen.blit(image, (0,0))
                    self.screen.blit(self.background_image, (320, 0))
                    self.screen.blit(self.forward_image, (350, 30))
                    self.screen.blit(self.backward_image, (350, 135))
                    self.screen.blit(self.left_image, (330, 77))
                    self.screen.blit(self.right_image, (380, 77))
                    self.screen.blit(self.stop_image, (350, 180))

                    pygame.display.update()
                    # select lower half of the image, region of interesting
                    #height, width = image.shape
                    #roi = image[int(height / 2):height, :]
                    #cv2.imshow('image', image)

                    end = cv2.getTickCount()
                # stream video frames one by one
                # get input from human driver
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Set the x, y postions of the mouse click
                        x, y = event.pos
                        #print(x,y)
                        if self.forward_image.get_rect(topleft=(350, 30)).collidepoint(x, y):
                            self.forward()
                        if self.backward_image.get_rect(topleft=(350, 135)).collidepoint(x, y):
                            self.backward()
                        if self.left_image.get_rect(topleft=(330, 77)).collidepoint(x, y):
                            self.left()
                        if self.right_image.get_rect(topleft=(380, 77)).collidepoint(x, y):
                            self.right()
                        if self.stop_image.get_rect(topleft=(350, 180)).collidepoint(x, y):
                            self.stop()

                    if event.type == pygame.MOUSEBUTTONUP:
                        # Set the x, y postions of the mouse click
                        x, y = event.pos
                        #print(x,y)
                        if self.left_image.get_rect(topleft=(330, 77)).collidepoint(x, y):
                            self.forward()
                        if self.right_image.get_rect(topleft=(380, 77)).collidepoint(x, y):
                            self.forward()
                        if self.backward_image.get_rect(topleft=(350, 135)).collidepoint(x, y):
                            self.stop()

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
                            #self.sock.send(chr(2).encode())
                            self.sock.send(chr(0).encode())

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

                    elif event.type == pygame.KEYUP and ( key_input[pygame.K_LEFT] or key_input[pygame.K_RIGHT]):
                        self.sock.send(chr(1).encode())
                        print("key up")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
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
            print("data:%s" % data)
            raw = re.match(r'\{(.*?)\}',data)
            print("raw:%s" % raw.group())
            text = json.loads(raw.group())
            return text

def ser_fun(SER,cardrive):
    #cardrive.forward()
    while True:
        try:
            j = SER.recv()
            #print(j)
            if j != None:
                if(j['cmd'] == 1):
                    cardrive.stop()
                    try:
                        requests.post("http://10.1.1.203:8080/getlist",{"position": j['pin']})
                    except:
                        print("post fail.")
                    sleep(2)
                if(j['cmd'] == 2):
                    cardrive.stop()
                    requests.post("http://10.1.1.203:8080/getlist", {"position": j['pin']})
                    sleep(j['time'] / 1000)
                    cardrive.forward()
        except Exception as e:
            print("reconnect serial. %s", e)
            SER.Serial_connect()
            sleep(1)

def light_time(SER):
    while True:
        sleep(10)
        try:
            j = requests.get("http://10.1.1.203:8080/getlist")
            light_time = j['time']
        except:
            print("get time fail.")

        try:
            SER.write(("^" + str(light_time) + "$").encode())
        except Exception as e:
            print("reconnect serial. %s", e)
            SER.Serial_connect()
            sleep(1)

if __name__ == '__main__':

    host_str = 'http://' + HOST + '/?action=stream'
    print ('Streaming ' + host_str)
    cardrive = CarDrive(host_str)
    SER = Ser()
    SER.Serial_connect()
    # vector size, half of the image
    s = 120 * 320
    _thread.start_new_thread( ser_fun, (SER,cardrive,) )
    _thread.start_new_thread( light_time, (SER,) )

    cardrive.key_drive()


