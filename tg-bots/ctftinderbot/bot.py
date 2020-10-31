import telebot
import random
import config
from pymongo import MongoClient
client = MongoClient()

bot = telebot.TeleBot(config.bot_token)
mongo = MongoClient(config.mongo_string)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if mongo.blitz_bot.blitz1406.find_one({"register_is_working": "True"}):
        text='''
Hello!
This is the Fargate team shuffling bot for blitz 14.06.
To register, send /register
To unregister, send /unregister
When the time comes, you will get a message with your teammate for this blitz.'''
        msg = bot.send_message(message.chat.id, text)
    else:
        msg = bot.send_message(message.chat.id, 'Register is closed')


@bot.message_handler(commands=['register'])
def send_auth(message):
    if mongo.blitz_bot.blitz1406.find_one({"register_is_working": "True"}):
        if mongo.blitz_bot.blitz1406.users.find_one({"username": message.chat.username}):
            msg = bot.send_message(message.chat.id, 'You alredy registered')
        else:
            mongo.blitz_bot.blitz1406.users.insert_one({'username': message.chat.username, 'chatid': message.chat.id})
            msg = bot.send_message(message.chat.id, 'Successfully registered')
            msg = bot.send_message(107177242, '@'+message.chat.username+' registered')
    else:
        msg = bot.send_message(message.chat.id, 'Register is closed')


@bot.message_handler(commands=['unregister'])
def send_auth(message):
    if mongo.blitz_bot.blitz1406.find_one({"register_is_working": "True"}):
        if mongo.blitz_bot.blitz1406.users.find_one({"username": message.chat.username}):
            mongo.blitz_bot.blitz1406.users.delete_one({"username": message.chat.username})
            msg = bot.send_message(message.chat.id, 'Successfully unregistered')
        else:
            msg = bot.send_message(message.chat.id, 'You are not registered')
    else:
        msg = bot.send_message(message.chat.id, 'Register is closed')


@bot.message_handler(commands=['stop_register_and_send_results'])
def send_auth(message):
    if mongo.blitz_bot.blitz1406.find_one({"register_is_working": "True"}):
        if message.chat.id == 107177242:
            mongo.blitz_bot.blitz1406.update({"register_is_working": "True"},{"register_is_working": "False"})
            msg = bot.send_message(message.chat.id, 'Successfully stopped the register')   
            msg = bot.send_message(message.chat.id, 'Results sended')     
            users = mongo.blitz_bot.blitz1406.users.find()
            userlist=[]
            pairs=[]
            for user in users:
                userlist.append(user["_id"])   
            random.shuffle(userlist)
            if len(userlist)%2==0:
                for i in range(0,int(len(userlist)/2)):
                    user1=mongo.blitz_bot.blitz1406.users.find_one({"_id": userlist.pop()})
                    user2=mongo.blitz_bot.blitz1406.users.find_one({"_id": userlist.pop()})
                    pairs.append(user1['username'] + ':' + str(user1['chatid']) + ' with ' + user2['username'] + ':' + str(user2['chatid']))
                    msg = bot.send_message(user1['chatid'], 'Hello, register is closed, your pair for this blitz is @'+user2['username'])   
                    msg = bot.send_message(user2['chatid'], 'Hello, register is closed, your pair for this blitz is @'+user1['username']) 
            if len(userlist)%2==1:
                for i in range(0,int((len(userlist)-1)/2)):
                    user1=mongo.blitz_bot.blitz1406.users.find_one({"_id": userlist.pop()})
                    user2=mongo.blitz_bot.blitz1406.users.find_one({"_id": userlist.pop()})
                    pairs.append(user1['username'] + ':' + str(user1['chatid']) + ' with ' + user2['username'] + ':' + str(user2['chatid']))
                    msg = bot.send_message(user1['chatid'], 'Hello, register is closed, your pair for this blitz is @'+user2['username'])   
                    msg = bot.send_message(user2['chatid'], 'Hello, register is closed, your pair for this blitz is @'+user1['username']) 
                msg = bot.send_message(mongo.blitz_bot.blitz1406.users.find_one({"_id": userlist.pop()})['chatid'], 'Hello, register is closed, and you don\'t have teammate for this blitz :^(((')   
            msg = bot.send_message(107177242, '\n'.join(pairs))
               
        else:
            msg = bot.send_message(message.chat.id, 'You are not the owner')
    else:
        msg = bot.send_message(message.chat.id, 'Register is closed')
    

@bot.message_handler(commands=['start_register'])
def send_auth(message):
    if message.chat.id == 107177242:
        mongo.blitz_bot.blitz1406.update({"register_is_working": "True"},{"register_is_working": "True"}, upsert= True)
        msg = bot.send_message(message.chat.id, 'Successfully started the register')            
    else:
        msg = bot.send_message(message.chat.id, 'You are not the owner')


bot.polling(none_stop=True)