import os
import schedule
import time
from threading import Timer, Thread
import json

from data.users import User
from data.chats import Chat
from data import db_session

REGISTER_PATH = 'files/incoming/register.encr'
LOGIN_PATH = 'files/incoming/login.encr'
DEFAULT_PHOTO_PATH = 'files/app_files/default.png'
DATA_BASE_PATH = 'db/my_encrypted.db'
CREATE_CHAT = 'files/incoming/create_chat.encr'
GET_CHATS = 'files/incoming/get_chats.encr'


def decent_data(data):
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
    response = f'files/outgoing/{file[0]}_create.encr'
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
                os.mkdir(f'files/users/{file[0]}/chats/{file[2]}')
                open(path, 'w', encoding='utf-8').write('[]')
            else:
                open(response, 'w', encoding='utf-8').write('404')
        else:
            open(response, 'w', encoding='utf-8').write('403')
    else:
        open(response, 'w', encoding='utf-8').write('404')
    data_session.close()
    t = Timer(15, delete_file, args=[response], kwargs=None)
    t.start()


def registration_procedure():
    file = open(REGISTER_PATH, 'r', encoding='utf-8').read().split()
    delete_file(REGISTER_PATH)
    data_session = db_session.create_session()
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
    response = f'files/outgoing/{file[1]}_reg.encr'
    open(response, 'w', encoding='utf-8').write('200')
    creating_user(file[1])
    t = Timer(15, delete_file, args=[response], kwargs=None)
    t.start()


def login_procedure():
    file = open(LOGIN_PATH, 'r', encoding='utf-8').read().split()
    delete_file(LOGIN_PATH)
    data_session = db_session.create_session()
    user = data_session.query(User).filter(User.login == file[0]).first()
    data_session.close()
    response = f'files/outgoing/{file[0]}_login.encr'
    if user:
        if user.check_password(file[1]):
            open(response, 'w', encoding='utf-8').write(
                f'{user.login} {user.name} {user.photo} {user.role}')
            t = Timer(15, delete_file, args=[response], kwargs=None)
            t.start()
            return 0
    open(response, 'w', encoding='utf-8').write('403')
    t = Timer(15, delete_file, args=[response], kwargs=None)
    t.start()


def get_chat_procedure():
    file = open(GET_CHATS, 'r', encoding='utf-8').read().split()
    delete_file(GET_CHATS)
    data_session = db_session.create_session()
    user = data_session.query(User).filter(User.login == file[0]).first()
    response = f'files/outgoing/{file[0]}_chats.encr'
    if user:
        if user.check_password(file[1]):
            chats = data_session.query(Chat).filter(Chat.creator == user.id or Chat.mate == user.id).all()
            chats = list(map(lambda x: decent_data(x), chats))
            open(response, 'w', encoding='utf-8').write(json.dumps(chats))
            t = Timer(15, delete_file, args=[response], kwargs=None)
            t.start()
            return 0
    open(response, 'w', encoding='utf-8').write('403')
    t = Timer(15, delete_file, args=[response], kwargs=None)
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


def main():
    db_session.global_init(DATA_BASE_PATH)
    schedule.every(1).seconds.do(scan)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
