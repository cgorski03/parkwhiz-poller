import telebot
import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


bot = telebot.TeleBot(BOT_TOKEN)

def send_message(message):
    """
    imported by other docs to send messages without request
    ret: null
    """
    bot.send_message(CHAT_ID, message)
