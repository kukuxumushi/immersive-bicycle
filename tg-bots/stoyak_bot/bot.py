import telebot
import random
import config
from pymongo import MongoClient
from time import sleep
from threading import Thread
import requests



client = MongoClient()
bot = telebot.TeleBot(config.bot_token)
mongo = MongoClient(config.mongo_string)
success_codes =[200, 201,202,203,204]

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
        text='''
Hello!
This bot alerts you when your desired site will go up.

To subscribe, send /subscribe https://example.com or with port if it is not default http://example.com:1234

To unsubscribe, send /unsubscribe https://example.com

To view your subscriptions, send /list

When the time comes, you will get a message.'''
        msg = bot.send_message(message.chat.id, text, disable_web_page_preview=True)
def extract_arg(arg):
    return arg.split()[1:]

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    argument = extract_arg(message.text)
    for site in argument:
        if mongo.stoyak.subscribe.find_one({"chatid": message.chat.id, 'website': site}):
            msg = bot.send_message(message.chat.id, 'You alredy subscribed to '+site, disable_web_page_preview=True)
        else:
            try:
                r = requests.get(site, allow_redirects=True, verify=False, timeout=10)
                if r.status_code in success_codes:
                    msg = bot.send_message(message.chat.id, site + ' is up! No subscription was created')
                    break
            except requests.exceptions.MissingSchema:
                site = 'http://'+site
                r = requests.get(site, allow_redirects=True, verify=False, timeout=10)
                if r.status_code in success_codes:
                    msg = bot.send_message(message.chat.id, site + ' is up! No subscription was created')
                    break
            except Exception as e:
                print(e)
                    
            mongo.stoyak.subscribe.insert_one({"chatid": message.chat.id, 'website': site})
            msg = bot.send_message(message.chat.id, 'Subscribed to '+site, disable_web_page_preview=True)
    
@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    argument = extract_arg(message.text)
    for site in argument:
        if mongo.stoyak.subscribe.find_one({"chatid": message.chat.id, 'website': site}):
            mongo.stoyak.subscribe.delete_one({"chatid": message.chat.id, 'website': site})
            msg = bot.send_message(message.chat.id, 'Unsubscribed from '+site, disable_web_page_preview=True)
        else:
            msg = bot.send_message(message.chat.id, 'You are not subscribed to '+site, disable_web_page_preview=True)
            
@bot.message_handler(commands=['list'])
def list(message):
    results = mongo.stoyak.subscribe.find({"chatid": message.chat.id})
    web_list=[]
    for result in results:
        web_list.append(result.get('website'))
    if web_list!=[]:
        msg = bot.send_message(message.chat.id, 'You subscribed to:\n'+'\n'.join(web_list))
    else:
       msg = bot.send_message(message.chat.id, 'You dont have any active subscriptions')


def threaded_function():
    while True:
        sites = mongo.stoyak.subscribe.find()
        for site in sites:
            try:
                r = requests.get(site.get('website'), allow_redirects=True, verify=False, timeout=30)
                print(site.get('website'))
                print(r)
                if r.status_code in success_codes:
                    msg = bot.send_message(site.get('chatid'), site.get('website') + ' is up!')
                    msg = bot.send_message(site.get('chatid'),  "\U0001F346")
                    mongo.stoyak.subscribe.delete_one({"chatid": site.get('chatid'), 'website': site.get('website')})
                    msg = bot.send_message(site.get('chatid'),  "Unsubscribed from "+ site.get('website'), disable_web_page_preview=True)   
            except Exception as e:
                print(site.get('website'))
                print(e)
        sleep(30)

thread = Thread(target = threaded_function)
thread.start()
bot.polling(none_stop=True)
