import telebot
from datetime import date
import pymongo
import bot_stats
import base64
import requests
import os
from config import token, api_key, mongoDB

# MongoDB
cluster = pymongo.MongoClient(mongoDB)
db4 = cluster["stats"]
statsData = db4["stats"]

bot = telebot.TeleBot(token)


def upload(doc_info, message):
	bot.send_message(message.chat.id, "*Downloading...*", parse_mode="Markdown")
	downloaded = bot.download_file(doc_info.file_path)
	output_name = doc_info.file_id
	f = open(output_name, 'wb')
	f.write(downloaded)

	with open(output_name, "rb") as image_file:
		encoded_string = base64.b64encode(image_file.read())

	bot.send_message(message.chat.id, "*Hosting on ImgBB...*", parse_mode="Markdown")
	host_response = requests.post(url="https://api.imgbb.com/1/upload", data={'key': api_key, 'image': encoded_string})
	
	if host_response.status_code == 200:
		host_url = host_response.json()["data"]["url"]
		bot.reply_to(message, f"*Successful!*\n`{host_url}`", parse_mode="Markdown")
	else:
		bot.reply_to(message, f"*{host_response.json()['error']['message']}*", parse_mode="Markdown")

	os.remove(output_name)


@bot.message_handler(content_types=['document'])
def document(message):
	doc_info = bot.get_file(message.document.file_id)
	upload(doc_info, message)
	bot_stats.send_stats(message, statsData, "document", date.isoformat(date.today()), bot)


@bot.message_handler(content_types=['photo'])
def photo(message):
	photo_info = bot.get_file(message.photo[-1].file_id)
	upload(photo_info, message)
	bot_stats.send_stats(message, statsData, "photo", date.isoformat(date.today()), bot)


@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, "📥 You can send an image as *forwarded message* from any chat/channel or upload it as *Photo* or *File*.", parse_mode="Markdown")
	bot_stats.send_stats(message, statsData, "start", date.isoformat(date.today()), bot)


if __name__ == '__main__':
    bot.infinity_polling()
