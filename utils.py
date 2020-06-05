from settings import *
import numpy as np
import tflearn

import os
from tflearn.layers.conv import conv_2d, max_pool_2d 
from tflearn.layers.core import input_data, dropout, fully_connected 
from tflearn.layers.estimator import regression 
import urllib.request as urllib2
    
import tensorflow as tf 
def create_model():
    tf.reset_default_graph() 
    convnet = input_data(shape =[None, IMG_SIZE, IMG_SIZE, 1], name ='input') 

    convnet = conv_2d(convnet, 32, 5, activation ='relu') 
    convnet = max_pool_2d(convnet, 5,) 

    convnet = conv_2d(convnet, 64, 5, activation ='relu') 
    convnet = max_pool_2d(convnet, 5) 

    convnet = conv_2d(convnet, 128, 5, activation ='relu') 
    convnet = max_pool_2d(convnet, 5) 

    convnet = conv_2d(convnet, 64, 5, activation ='relu') 
    convnet = max_pool_2d(convnet, 5) 

    convnet = conv_2d(convnet, 32, 5, activation ='relu') 
    convnet = max_pool_2d(convnet, 5) 

    convnet = fully_connected(convnet, 1024, activation ='relu') 
    convnet = dropout(convnet, 0.8) 

    convnet = fully_connected(convnet, 2, activation ='softmax') 
    convnet = regression(convnet, optimizer ='adam', learning_rate = LR, 
        loss ='categorical_crossentropy', name ='targets') 

    model = tflearn.DNN(convnet, tensorboard_dir ='log') 
    return model


def send_sms():
    from twilio.rest import Client
    client=Client(ACC_SID,AUTH_TOKEN)
    client.messages.create(to=Reg_Num,from_=Twilio_Num,body=message)
    return 1


def internet_on():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib2.URLError as err: 
        return False
