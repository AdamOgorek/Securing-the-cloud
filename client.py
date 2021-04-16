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

while(True):
    text = input("upload or download?\n")
    if(text == "upload"):
        path_on_cloud = input("What path to upload?\n")
        print(path_on_cloud)
        path_on_device = input("Which file to upload?\n")
        cloud.child("test2.txt").put(path_on_device)
        print("done")
    elif(text == "download"):
        path_on_cloud = input("Which file to download?\n")
        path_on_device = input("Where to download?\n")
        cloud.child(path_on_cloud).download(path_on_device)
        print("done")
    else:
        print("Error")

