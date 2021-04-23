import pyrebase
import json
import os
import socket
import request_types
import ssl
from requests.exceptions import HTTPError
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

HOST = '127.0.0.1'
PORT = 5000


def create_account():
    email = input("What is your email?\n")
    password = input("What is your password?\n")
    auth = firebase.auth()
    try:
        temp_user = auth.create_user_with_email_and_password(email, password)
        return temp_user
    except HTTPError as err:
        print(json.loads(err.args[1])['error']['message'])


def login():
    email = input("What is your email?\n")
    password = input("What is your password?\n")
    auth = firebase.auth()
    try:
        temp_user = auth.sign_in_with_email_and_password(email, password)
        return temp_user
    except HTTPError as err:
        print(json.loads(err.args[1])['error']['message'])


def encrypt_file(filepath):
    file_in = open(filepath, "rb")
    data = file_in.read()
    cipher = AES.new(key, AES.MODE_EAX)
    encrypted_file, tag = cipher.encrypt_and_digest(data)

    file_out = open("temp.bin", "wb")
    [file_out.write(x) for x in (cipher.nonce, tag, encrypted_file)]
    file_out.close()


def decrypt_file(filepath):
    file_out = open(filepath, "rb")
    nonce, tag, encrypted_data = [file_out.read(x) for x in (16, 16, -1)]
    file_out.close()
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)
    os.remove(filepath)

    decrypted_file = open(filepath, 'wb')
    decrypted_file.write(decrypted_data)
    decrypted_file.close()


def create_group(groupid):
    context = ssl.create_default_context(cafile = 'cert.pem')
    client_socket = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = "Adam")
    try:
        client_socket.connect((HOST, PORT))
    except socket.error as err:
        print(str(err))
    message_str = chr(request_types.CREATE_GROUP_REQUEST)
    padding_needed = 64-len(groupid)
    message_str += ('\0'*padding_needed)
    message_str += groupid
    message_str += user['idToken']
    request = message_str.encode('utf-8')
    client_socket.sendall(request)
    response = client_socket.recv(2048)
    print(response.decode('utf-8'))


def add_user(groupid, user_to_add):
    context = ssl.create_default_context(cafile = 'cert.pem')
    client_socket = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = "Adam")
    try:
        client_socket.connect((HOST, PORT))
    except socket.error as err:
        print(str(err))
    message_str = chr(request_types.ADD_USER_TO_GROUP_REQUEST)
    padding_needed = 64 - len(groupid)
    message_str += ('\0' * padding_needed)
    message_str += groupid
    padding_needed = 64 - len(user_to_add)
    message_str += ('\0' * padding_needed)
    message_str += user_to_add
    message_str += user['idToken']
    request = message_str.encode('utf-8')
    client_socket.sendall(request)
    response = client_socket.recv(2048)
    print(response.decode('utf-8'))


def get_key(groupid):
    context = ssl.create_default_context(cafile = 'cert.pem')
    client_socket = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname = "Adam")
    try:
        client_socket.connect((HOST, PORT))
    except socket.error as err:
        print(str(err))
    message_str = chr(request_types.GET_KEY_REQUEST)
    padding_needed = 64 - len(groupid)
    message_str += ('\0' * padding_needed)
    message_str += groupid
    message_str += user['idToken']
    request = message_str.encode('utf-8')
    client_socket.sendall(request)
    response = client_socket.recv(2048)
    if response[1] == 1:
        return response[2:]
    else:
        return 0


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



key = b''
last_group = ''
user = None
while user is None:
    text = input("Login or sign up?\n")
    if text == "login":
        user = login()
    elif text == "sign up":
        user = create_account()
    else:
        print("Try again")

#cloud.child("test.txt").download("xd.txt", user['idToken'])

while True:
    text = input("Manage groups or files?\n")
    if text == '1':
        input2 = input("Create group or add user?\n")
        if input2 == '1':
            group_name = input("What name for the group?\n")
            create_group(group_name)
        else:
            group_name = input("What name for the group?\n")
            user_email = input("What is the email of the user?\n")
            add_user(group_name, user_email)
    elif text == '2':
        group_name = input("What group?\n")
        if group_name != last_group:
            key = get_key(group_name)
        if key != 0:
            last_group = group_name
            input2 = input("Upload or download?\n")
            if input2 == '1':
                path_on_cloud = input("Please give the path where you wish to upload\n")
                path_on_device = input("Please give the path to the file you want to upload\n")
                encrypt_file(path_on_device)
                cloud.child(group_name).child(path_on_cloud).put("temp.bin", user['idToken'])
                os.remove("temp.bin")
            else:
                path_on_cloud = input("Please give the path you wish to download\n")
                path_on_device = input("Please give the path where to download the file\n")
                cloud.child(group_name).child(path_on_cloud).download(path_on_device, user['idToken'])
                decrypt_file(path_on_device)
    elif text == 'quit':
        break
    else:
        print("wrong input")
