import logging
import re
import requests
import random
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logins = ['Chad Jacobs',
'Clara Nichols',
'Blade Odling',
'Kaylen Summers',
'Patrik Walters',
'Keyaan Thompson',
'Anaiya Roche',
'Alannah Nicholson',
'Tommy Lennon',
'Kerry Dunn','Emilio Rosario',
'Tomasz Weaver',
'Ashlea Vargas',
'Keeva Crouch',
'Alyce Woodard',
'Tyrone Moon',
'Aliya Atkinson',
'Zaydan Huffman',
'Nabilah Steadman',
'Kourtney Houghton']

texts = ['Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua',
'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
'Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
'Donec et odio pellentesque diam volutpat commodo sed egestas egestas.',
'Ultrices in iaculis nunc sed augue lacus viverra vitae.']

def sign_up(login, password):
    url = 'http://127.0.0.1:5000/register'
    data = {'login': login, 'password': password}
    req = requests.post(url, json = data)
    #print(req.json())

def sign_in(login, password):
    url = 'http://127.0.0.1:5000/login'
    req = requests.post(url, auth=requests.auth.HTTPBasicAuth(login, password))
    #print(req.json())
    req = req.json()
    print(req)
    token = req['token']
    token = token.replace('Bearer ','')
    return token

def create_post(token, text):
    url = 'http://127.0.0.1:5000/create_post'
    data = {'text': text}
    headers = {'Authorization': 'Bearer ' + token}
    req = requests.post(url, json = data, headers = headers)
    #print(req.json())

def like(token, post_id):
    url = 'http://127.0.0.1:5000/like'
    data = {'id': post_id}
    headers = {'Authorization': 'Bearer ' + token}
    req = requests.post(url, json = data, headers = headers)
    #print(req.json())

def get_posts(token):
    url = 'http://127.0.0.1:5000/posts'
    headers = {'Authorization': 'Bearer ' + token}
    req = requests.get(url, headers = headers)
    #print(req.json())
    req = req.json()
    posts = req['posts']
    return posts

def bot():
    file = open('config.txt', 'r')
    lines = file.readlines()

    for line in lines:
        if re.search('number_of_users', line):
            number_of_users = line.replace('number_of_users = ', '')
            number_of_users = int(number_of_users)

        if re.search('max_posts_per_user', line):
            max_posts_per_user = line.replace('max_posts_per_user = ', '')
            max_posts_per_user = int(max_posts_per_user)

        if re.search('max_likes_per_user', line):
            max_likes_per_user = line.replace('max_likes_per_user = ', '')
            max_likes_per_user = int(max_likes_per_user)

    while number_of_users != 0:
        login = random.choice(logins) + ' ' + random.choice(logins)
        password = random.choice(logins)
        print('login ',login)
        print('password ',password)
        posts = random.randint(1, max_posts_per_user)
        likes = random.randint(1, max_likes_per_user)
        sign_up(login, password)
        token = sign_in(login, password)
        while posts != 0:
            text = random.choice(texts)
            create_post(token, text)
            posts -= 1
        while likes != 0:
            post_id = random.randint(1, get_posts(token))
            like(token, post_id)
            likes -= 1
        number_of_users -= 1

if __name__=='__main__':
    bot()
