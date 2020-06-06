
from flask import Flask, flash, request, json,render_template, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from settings import *
from utils import *
from cv2 import imread,resize,IMREAD_GRAYSCALE,CAP_PROP_POS_MSEC, VideoCapture,imwrite
import numpy as np
import os
import shutil
import base64  
from cryptography.hazmat.backends import default_backend 
from cryptography.hazmat.primitives import hashes 
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_IMAGE_FOLDER'] = UPLOAD_IMAGE_FOLDER
app.config['UPLOAD_VIDEO_FOLDER'] = UPLOAD_VIDEO_FOLDER

app.secret_key = 'some_secret'
signed_in=0
@app.route('/')
def index():
    signed_in=1
    return render_template('./index.html')

@app.route('/',methods=['GET','POST'])


def validate_login():
    if request.method == 'POST':
        password=request.form['password']
        username=request.form['id']
        password_provided=password
        password = password_provided.encode()
        username_provided=username
        username=username_provided.encode()
        salt = b'salt_' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes 
        kdf = PBKDF2HMAC( algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend() ) 
        key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once
        password_generated=key
        kdf = PBKDF2HMAC( algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend() ) 
        key = base64.urlsafe_b64encode(kdf.derive(username)) # Can only use kdf once
        username_generated=key
        
        file = open('pass.key', 'rb') 
        key1 = file.read() # The key will be type bytes 
        file.close()
        file = open('user.key', 'rb') 
        key2 = file.read() # The key will be type bytes 
        file.close()

        if (key1 == password_generated and key2 == username_generated):
            return render_template('./main.html')
        else:
            value=1
            return render_template('./index.html',value=value)


@app.route('/main.html', methods=['GET', 'POST'])

def make_prediction():
    """View that receive images and render predictions
    """
    

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
       
        
        filename = secure_filename(file.filename)
        extension= filename.rsplit('.', 1)[1].lower()
        if extension in ALLOWED_IMAGE_EXTENSIONS:
           
            file_path = save_image(file, filename)
            path = os.path.join(PROJECT_PATH,file_path) 
            model=create_model()
            model.load('./crack_detection_model')
            img=imread(path,IMREAD_GRAYSCALE)
            img = resize(img, (IMG_SIZE, IMG_SIZE)) 
            orig = np.array(img)
            data = orig.reshape(IMG_SIZE, IMG_SIZE, 1) 
            model_out = model.predict([data])[0]
            if np.argmax(model_out) == 1: str_label ='Cracked'
            else: str_label ='Uncracked'
            test_net=internet_on()
            
            if str_label == 'Cracked':
                if  test_net :
                    value= send_sms()
                    return render_template('main.html',str_label=str_label,cur_image_path=file_path,value=value)
                return render_template('main.html',str_label=str_label,cur_image_path=file_path)
            else:
                return render_template('main.html',str_label=str_label,cur_image_path=file_path)

        elif extension in ALLOWED_VIDEO_EXTENSIONS:
            
            
            file_path = save_video(file, filename)
            path = os.path.join(PROJECT_PATH,file_path)
            model=create_model()
            model.load('./crack_detection_model')
            process_video(path)
            
            
            for img in os.listdir(VID_T0_IMG_FOLDER):
      
                path="./static/shots/"+img
                img=imread(path,IMREAD_GRAYSCALE)
                img = resize(img, (IMG_SIZE, IMG_SIZE)) 
                orig = np.array(img)
                data = orig.reshape(IMG_SIZE, IMG_SIZE, 1) 
                model_out = model.predict([data])[0]
                if np.argmax(model_out) == 1: 
                    str_label ='Cracked'
                    break
                        
                else: 
                    str_label ='Uncracked'
                
            imwrite("./static/temp/temp.png",imread(path))
            path_temp="./static/temp/temp.png"
##            mypath = "./static/shots"
##            for root, dirs, files in os.walk(mypath):
##                for file in files:
##                    os.remove(os.path.join(root, file))
            
            value=False
            
            if str_label == 'Cracked':
                value= send_sms()
                return render_template('main.html',str_label=str_label,cur_image_path=path_temp,value=value)
            else:
                return render_template('main.html',str_label=str_label,cur_image_path=path_temp)


        else:
            err=1
            return render_template('main.html',err=err)


    

def save_image(file, filename):
    
    # create folder for storing images if not exist
    if not os.path.exists(app.config['UPLOAD_IMAGE_FOLDER']):
        os.makedirs(app.config['UPLOAD_IMAGE_FOLDER'])

    # save image locally
    file_path = os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], filename)
    file.save(file_path)

  
    return file_path
def save_video(file,filename):

    if not os.path.exists(app.config['UPLOAD_VIDEO_FOLDER']):
        os.makedirs(app.config['UPLOAD_VIDEO_FOLDER'])
        
    file_path = os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], filename)
    file.save(file_path)
    return file_path

def process_video(path):
    vidcap = VideoCapture(path)
    def getFrame(sec):
        vidcap.set(CAP_PROP_POS_MSEC,sec*1000)
        hasFrames,image = vidcap.read()
        if hasFrames:
            imwrite("static/shots/image"+str(count)+".jpg", image)     # save frame as JPG file
        return hasFrames
    sec = 0
    frameRate = 2 #//it will capture image in each 2 seconds
    count=1
    success = getFrame(sec)
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success = getFrame(sec)
    return 

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404






        
    

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port,debug=IS_DEBUG,threaded=True)
