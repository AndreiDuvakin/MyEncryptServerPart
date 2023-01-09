import os
import schedule
import time
from threading import Timer
import json

import sqlalchemy.testing

from data.users import User
from data.chats import Chat
from data import db_session

REGISTER_PATH = '/home/visitor/incoming/register.encr'
LOGIN_PATH = '/home/visitor/incoming/login.encr'
DEFAULT_PHOTO_PATH = 'files/app_files/default.png'
DATA_BASE_PATH = 'db/my_encrypted.db'
CREATE_CHAT = '/home/visitor/incoming/create_chat.encr'
GET_CHATS = '/home/visitor/incoming/get_chats.encr'
GET_NEW_CHAT = '/home/visitor/incoming/get_new_chat.encr'
CHECK_LOGIN = '/home/visitor/incoming/check_login.encr'
GET_DATA_USER = '/home/visitor/incoming/get_data_users.encr'
CHANGE_USER_DATA = '/home/visitor/incoming/change_user_data.encr'


def decent_data_get_chats(data):
    data_session = db_session.create_session()
    creator = data_session.query(User).filter(User.id == data.creator).first()
    mate = data_session.query(User).filter(User.id == data.mate).first()
    resp = [data.id, [creator.id, creator.name, creator.login], [mate.id, mate.name, mate.login], data.path]
    data_session.close()
    return resp


def creating_user(login):
    os.mkdir(f'files/users/{login}')
    os.mkdir(f'files/users/{login}/chats')


def delete_file(path):
    os.remove(path)


def create_chat_procedure():
    file = open(CREATE_CHAT, 'r', encoding='utf-8').read().split()
    delete_file(CREATE_CHAT)
    data_session = db_session.create_session()
    creator = data_session.query(User).filter(User.login == file[0]).first()
    response = f'/home/visitor/outgoing/{file[0]}_create.encr'
    if creator:
        if creator.check_password(file[1]):
            mate = data_session.query(User).filter(User.login == file[2]).first()
            data_session.close()
            if mate:
                path = f'files/users/{file[0]}/chats/{file[2]}.encr'
                chat = Chat(
                    creator=creator.id,
                    mate=mate.id,
                    path=path
                )
                data_session = db_session.create_session()
                data_session.add(chat)
                data_session.commit()
                data_session.close()
                open(path, 'w', encoding='utf-8').write('[]')
                open(response, 'w', encoding='utf-8').write('200')
            else:
                open(response, 'w', encoding='utf-8').write('404')
        else:
            open(response, 'w', encoding='utf-8').write('403')
    else:
        open(response, 'w', encoding='utf-8').write('404')
    data_session.close()
    t = Timer(5, delete_file, args=[response], kwargs=None)
    t.start()


def registration_procedure():
    file = open(REGISTER_PATH, 'r', encoding='utf-8').read().split()
    delete_file(REGISTER_PATH)
    data_session = db_session.create_session()
    try:
        user = User(
            name=file[0],
            login=file[1],
            role='user',
            photo=DEFAULT_PHOTO_PATH
        )
        user.set_password(file[2])
        data_session.add(user)
        data_session.commit()
        data_session.close()
        response = f'/home/visitor/outgoing/{file[1]}_reg.encr'
        open(response, 'w', encoding='utf-8').write('200')
        creating_user(file[1])
        t = Timer(5, delete_file, args=[response], kwargs=None)
        t.start()
    except IndexError as e:
        print(file, e)
        response = f'/home/visitor/outgoing/{file[1]}_reg.encr'
        open(response, 'w', encoding='utf-8').write('error')
        t = Timer(5, delete_file, args=[response], kwargs=None)
        t.start()


def login_procedure():
    try:
        file = open(LOGIN_PATH, 'r', encoding='utf-8').read().split()
        delete_file(LOGIN_PATH)
        data_session = db_session.create_session()
        user = data_session.query(User).filter(User.login == file[0]).first()
        data_session.close()
        response = f'/home/visitor/outgoing/{file[0]}_login.encr'
        if user:
            if user.check_password(file[1]):
                open(response, 'w', encoding='utf-8').write(
                    f'{user.login} {user.name} {user.photo} {user.role}')
                t = Timer(5, delete_file, args=[response], kwargs=None)
                t.start()
                return 0
        open(response, 'w', encoding='utf-8').write('403')
        t = Timer(5, delete_file, args=[response], kwargs=None)
        t.start()
    except IndexError:
        pass


def get_chat_procedure():
    file = open(GET_CHATS, 'r', encoding='utf-8').read().split()
    delete_file(GET_CHATS)
    data_session = db_session.create_session()
    user = data_session.query(User).filter(User.login == file[0]).first()
    response = f'/home/visitor/outgoing/{file[0]}_chats.encr'
    if user:
        if user.check_password(file[1]):
            chats = data_session.query(Chat).filter(Chat.creator == user.id).all() + data_session.query(Chat).filter(
                Chat.mate == user.id).all()
            chats = list(map(lambda x: decent_data_get_chats(x), chats))
            open(response, 'w', encoding='utf-8').write(json.dumps(chats))
            data_session.close()
            t = Timer(5, delete_file, args=[response], kwargs=None)
            t.start()
            return 0
    data_session.close()
    open(response, 'w', encoding='utf-8').write('403')
    t = Timer(5, delete_file, args=[response], kwargs=None)
    t.start()


def get_new_chat_procedure():
    file = open(GET_NEW_CHAT, 'r', encoding='utf-8').read().split()
    delete_file(GET_NEW_CHAT)
    data_session = db_session.create_session()
    user = data_session.query(User).filter(User.login == file[0]).first()
    response = f'/home/visitor/outgoing/{file[0]}_new_chat.encr'
    if user:
        if user.check_password(file[1]):
            maters = list(map(lambda x: x[0], data_session.query(Chat.mate).filter(Chat.creator == user.id).all()))
            users = list(map(lambda x: [x.id, x.name, x.login, x.role, x.photo],
                             data_session.query(User).filter(User.id.not_in(maters), User.id != user.id).all()))
            open(response, 'w', encoding='utf-8').write(json.dumps(users))
            data_session.close()
            t = Timer(5, delete_file, args=[response], kwargs=None)
            t.start()
            return 0
    data_session.close()
    open(response, 'w', encoding='utf-8').write('403')
    t = Timer(5, delete_file, args=[response], kwargs=None)
    t.start()


def check_login_procedure():
    file = open(CHECK_LOGIN, 'r', encoding='utf-8').read()
    delete_file(CHECK_LOGIN)
    data_session = db_session.create_session()
    user = data_session.query(User).filter(User.login == file).first()
    data_session.close()
    response = f'/home/visitor/outgoing/{file}_check_login.encr'
    if user:
        open(response, 'w', encoding='utf-8').write('200')
    else:
        open(response, 'w', encoding='utf-8').write('404')
    t = Timer(5, delete_file, args=[response], kwargs=None)
    t.start()


def get_data_user():
    file = open(GET_DATA_USER, 'r', encoding='utf-8').read().split()
    delete_file(GET_DATA_USER)
    data_session = db_session.create_session()
    user = data_session.query(User).filter(User.login == file[0]).first()
    data_session.close()
    response = f'/home/visitor/outgoing/{file[0]}_get_data_user.encr'
    if user:
        if user.check_password(file[1]):
            open(response, 'w', encoding='utf-8').write(json.dumps([user.id, user.name, user.login, user.role]))
            t = Timer(5, delete_file, args=[response], kwargs=None)
            t.start()
            return 0
    open(response, 'w', encoding='utf-8').write('403')
    t = Timer(5, delete_file, args=[response], kwargs=None)
    t.start()


def change_user_dats():
    file = open(CHANGE_USER_DATA, 'r', encoding='utf-8').read().split()
    delete_file(CHANGE_USER_DATA)
    data_session = db_session.create_session()
    user = data_session.query(User).filter(User.login == file[0]).first()
    response = f'/home/visitor/outgoing/{file[0]}_change_user_data.encr'
    if user:
        if user.check_password(file[1]):
            if file[2] == 'name':
                user.name = file[3]
            elif file[2] == 'password':
                user.set_password(file[3])
            elif file[2] == 'photo':
                pass
            else:
                open(response, 'w', encoding='utf-8').write('412')
                t = Timer(5, delete_file, args=[response], kwargs=None)
                t.start()
                return 0
            open(response, 'w', encoding='utf-8').write('200')
            data_session.commit()
            data_session.close()
            t = Timer(5, delete_file, args=[response], kwargs=None)
            t.start()
            return 0
    data_session.close()
    open(response, 'w', encoding='utf-8').write('403')
    t = Timer(5, delete_file, args=[response], kwargs=None)
    t.start()


def scan():
    find = os.path.exists(REGISTER_PATH)
    if find:
        t = Timer(0, registration_procedure, args=None, kwargs=None)
        t.start()
    find = os.path.exists(LOGIN_PATH)
    if find:
        t = Timer(0, login_procedure, args=None, kwargs=None)
        t.start()
    find = os.path.exists(CREATE_CHAT)
    if find:
        t = Timer(0, create_chat_procedure, args=None, kwargs=None)
        t.start()
    find = os.path.exists(GET_CHATS)
    if find:
        t = Timer(0, get_chat_procedure, args=None, kwargs=None)
        t.start()
    find = os.path.exists(GET_NEW_CHAT)
    if find:
        t = Timer(0, get_new_chat_procedure, args=None, kwargs=None)
        t.start()
    find = os.path.exists(CHECK_LOGIN)
    if find:
        t = Timer(0, check_login_procedure, args=None, kwargs=None)
        t.start()
    find = os.path.exists(GET_DATA_USER)
    if find:
        t = Timer(0, get_data_user, args=None, kwargs=None)
        t.start()
    find = os.path.exists(CHANGE_USER_DATA)
    if find:
        t = Timer(0, change_user_dats, args=None, kwargs=None)
        t.start()


def main():
    db_session.global_init(DATA_BASE_PATH)
    schedule.every(1).seconds.do(scan)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
