import os 
IMG_SIZE = 50       
    
LR = 1e-3
UPLOAD_IMAGE_FOLDER = 'static/uploaded_images'
UPLOAD_VIDEO_FOLDER = 'static/uploaded_videos'
VID_T0_IMG_FOLDER = 'static/shots'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
IS_DEBUG = True
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ALLOWED_VIDEO_EXTENSIONS = set(['mov','mp4','avi'])
ACC_SID=""
AUTH_TOKEN=""
Twilio_Num=""
Reg_Num=""
message="Crack detected       location : XXXXXXX  . Require immediate action."
