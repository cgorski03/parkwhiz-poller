import subprocess
import telebot
from env import BOT_TOKEN, CHAT_ID


bot = telebot.TeleBot(BOT_TOKEN)

def send_message(message):
    """
    imported by other docs to send messages without request
    ret: null
    """
    bot.send_message(CHAT_ID, message)
