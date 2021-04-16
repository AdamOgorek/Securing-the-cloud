import pyrebase

config = {
    "apiKey": "AIzaSyBtb-VLcnojAkq-0xZBGnCC0Dn08D4qq2w",
    "authDomain": "the-cloud-a6f47.firebaseapp.com",
    "projectId": "the-cloud-a6f47",
    "databaseURL": "https://the-cloud-a6f47-default-rtdb.europe-west1.firebasedatabase.app/",
    "storageBucket": "the-cloud-a6f47.appspot.com",
    "messagingSenderId": "875416688354",
    "appId": "1:875416688354:web:b57075c1316879f61ab0bb",
    "measurementId": "G-4LBT7CKYWN"
}

firebase = pyrebase.initialize_app(config)

cloud = firebase.storage()

cloud.child("test/test.txt").put("testujemy.txt")

cloud.child("test/test.txt").download("downtest.txt")

