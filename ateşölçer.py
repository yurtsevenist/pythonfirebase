import RPi.GPIO as GPIO
import time
from smbus2 import SMBus
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from mlx90614 import MLX90614

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = 23
ECHO = 24
LASER=17
SES=25

print ("HC-SR04 mesafe sensoru")

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(LASER,GPIO.OUT)
GPIO.setup(SES,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

# Firebase Credential json dosyanızı bu projeyle aynı klasöre koyun ve adını "serviceAccountKey.json" yapın
cred = credentials.Certificate("serviceAccount.json")
# Firebase Database URL'inizi ekleyin
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ihmbilisim-a2e6b.firebaseio.com'
})

while True:

 GPIO.output(TRIG, False)
 print ("Olculuyor...")
 time.sleep(2)

 GPIO.output(TRIG, True)
 time.sleep(0.00001)
 GPIO.output(TRIG, False)
 GPIO.output(17,GPIO.LOW)
 GPIO.output(25,GPIO.LOW)
 while GPIO.input(ECHO)==0:
     pulse_start = time.time()

 while GPIO.input(ECHO)==1:
     pulse_end = time.time()

 pulse_duration = pulse_end - pulse_start

 distance = pulse_duration * 17150
 distance = round(distance, 2)
 
 if distance > 5 and distance < 100:
     print ("Mesafe:",distance - 0.5,"cm")
     GPIO.output(17,GPIO.LOW)
     GPIO.output(25,GPIO.LOW)
 elif(distance <=5):
     print ("Ateş Ölçülüyor....")
     ref = db.reference("/bilgiler")
     bilgi = ref.get()
     GPIO.output(17,GPIO.HIGH)
     GPIO.output(25,GPIO.HIGH)
     for key, value in bilgi.items():
        if(value["kategori"] == "ateş"):
            #print(value["bilgi"])
            #value["bilgi"] = 90
            ref.child(key).update({"bilgi":"?"})
            ref.child(key).update({"yorum":"Ateşiniz Ölçülüyor..."})
     time.sleep(2)
     bus = SMBus(1)
     sensor = MLX90614(bus, address=0x5a)
     #print (sensor.get_ambient())
     #print (sensor.get_object_1())
     ortam = "{:.1f}".format(sensor.get_ambient())
     insan = "{:.1f}".format(sensor.get_object_1())
     ortamC = float(ortam)
     insanC = float(insan)
     print("Ortam Sıcaklığı: {} °C".format(ortamC))
     print("İnsan Sıcaklığı: {} °C".format(insanC))
     bus.close()
     if(insanC>=38):
         yorum="Ateşiniz Yüksek"
     else:
         yorum="Ateşiniz Normal"
     ortamS=str(ortamC)+" °C"
     for key, value in bilgi.items():
        if(value["kategori"] == "ateş"):
            #print(value["bilgi"])
            #value["bilgi"] = 90
            ref.child(key).update({"bilgi":ortamS})
            ref.child(key).update({"yorum":yorum})
     time.sleep(1)
     