import pyrebase
import os
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes



def encrypt_file(filename):
    file_in = open(filename,"rb")
    data = file_in.read()
    cipher = AES.new(key, AES.MODE_EAX)
    encrypted_file, tag = cipher.encrypt_and_digest(data)

    file_out = open("encrypted_" + filename, "wb")
    [ file_out.write(x) for x in (cipher.nonce, tag, encrypted_file) ]
    file_out.close()

def decrypt_file(filename):
    file_out = open(filename, "rb")
    nonce, tag, encrypted_data = [ file_out.read(x) for x in (16, 16, -1) ]
    file_out.close()
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)
    os.remove(filename)

    decrypted_file = open(filename, 'wb')
    decrypted_file.write(decrypted_data)
    decrypted_file.close()


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
key = get_random_bytes(16)



while(True):
    text = input("upload or download?\n")
    if(text == "upload"):
        path_on_cloud = input("What path to upload?\n")
        path_on_device = input("Which file to upload?\n")
        encrypt_file(path_on_device)
        cloud.child(path_on_cloud).put("encrypted_" + path_on_device)
        os.remove("encrypted_" + path_on_device)
        print("done")
    elif(text == "download"):
        path_on_cloud = input("Which file to download?\n")
        path_on_device = input("Where to download?\n")
        cloud.child(path_on_cloud).download(path_on_device)
        decrypt_file(path_on_device)
        print("done")
    else:
        print("Error")
