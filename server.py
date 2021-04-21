import pyrebase
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import socket
from _thread import *
import request_types
import re
PORT = 5000
HOST = '127.0.0.1'


def create_group(groupid, ownerid):
    db = firebase.database()
    key = get_random_bytes(16)
    if db.child("groups").child(groupid).get(admin['idToken']).val() is None:
        db.child("groups").child(groupid).child("ownerID").set(ownerid, admin['idToken'])
        key_list = []
        for byte in key:
            key_list.append(byte)
        db.child("groups").child(groupid).child("key").set(key_list, admin['idToken'])
        add_user(groupid, ownerid)
        return True
    else:
        return False


def add_user(groupid, userid):
    db = firebase.database()
    users = db.child("group members").child(groupid).child("users").get(admin['idToken']).val()
    if users is not None:
        if userid not in users:
            users.append(userid)
            db.child("group members").child(groupid).child("users").set(users, admin['idToken'])
            return True
        else:
            return False
    else:
        users = [userid]
        db.child("group members").child(groupid).child("users").set(users, admin['idToken'])
        return True


def get_key(groupid, userid):
    db = firebase.database()
    users = db.child("group members").child(groupid).child("users").get(admin['idToken'])
    if userid in [x.val() for x in users.each()]:
        key = db.child("groups").child(groupid).child("key").get(admin['idToken']).val()
        return key
    else:
        return 0


def check_group_owner(groupid):
    db = firebase.database()
    owner = db.child("groups").child(groupid).child("ownerID").get(admin['idToken']).val()
    return owner


def threaded_client(connection):
    data = connection.recv(2048)
    if data != b'':
        if data[0] == request_types.CREATE_GROUP_REQUEST:
            groupid = re.sub('\0', '', data[1:65].decode('utf-8'))
            user_token = data[65:].decode('utf-8')
            user_info = auth.get_account_info(user_token)
            user_email = user_info['users'][0]['email']
            success = create_group(groupid, user_email)
            if success:
                response_str = chr(request_types.CREATE_GROUP_REQUEST)
                response_str += '\x01Success!'
                connection.sendall(response_str.encode('utf-8'))
            else:
                response_str = chr(request_types.CREATE_GROUP_REQUEST)
                response_str += '\x00Group already exists.'
                connection.sendall(response_str.encode('utf-8'))
        elif data[0] == request_types.ADD_USER_TO_GROUP_REQUEST:
            groupid = re.sub('\0', '', data[1:65].decode('utf-8'))
            userid = re.sub('\0', '', data[65:129].decode('utf-8'))
            user_token = data[129:].decode('utf-8')
            user_info = auth.get_account_info(user_token)
            user_email = user_info['users'][0]['email']
            if user_email == check_group_owner(groupid):
                success = add_user(groupid, userid)
                if success:
                    response_str = chr(request_types.ADD_USER_TO_GROUP_REQUEST)
                    response_str += '\x01Success!'
                    connection.sendall(response_str.encode('utf-8'))
                else:
                    response_str = chr(request_types.ADD_USER_TO_GROUP_REQUEST)
                    response_str += '\x00User already in that group.'
                    connection.sendall(response_str.encode('utf-8'))
            else:
                response_str = chr(request_types.ADD_USER_TO_GROUP_REQUEST)
                response_str += '\x00Only the owner can add to group'
                connection.sendall(response_str.encode('utf-8'))
        elif data[0] == request_types.GET_KEY_REQUEST:
            groupid = re.sub('\0', '', data[1:65].decode('utf-8'))
            user_token = data[65:].decode('utf-8')
            user_info = auth.get_account_info(user_token)
            user_email = user_info['users'][0]['email']
            key = get_key(groupid, user_email)
            if key != 0:
                encrypted_key = ''
                response_str = chr(request_types.GET_KEY_REQUEST)
                response_str += '\x01'
                #add encrypted key to response
                connection.sendall(response_str.encode('utf-8'))
            else:
                response_str = chr(request_types.GET_KEY_REQUEST)
                response_str += '\x00User not in that group.'
                connection.sendall(response_str.encode('utf-8'))
        else:
            connection.send(str.encode("Wrong request"))
    connection.close()


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
auth = firebase.auth()
admin = auth.sign_in_with_email_and_password("ogoreka@tcd.ie", "123456")

server = socket.socket()
try:
    server.bind((HOST, PORT))
except socket.error as err:
    print(str(err))
print('waiting')
server.listen(5)
while True:
    client, address = server.accept()
    print('new connection')
    start_new_thread(threaded_client, (client, ))

server.close()
