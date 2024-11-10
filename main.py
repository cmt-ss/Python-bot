import time
import json
import telebot
import random

# Token and constants
BOT_TOKEN = "7462875981:AAGmUrEzKk75j7XjuPSVuAGiT2_drDdLv_0"
Daily_bonus = 0.5
Mini_Withdraw = 1
Per_Refer = 0.5
Game_reward = 0.001

bot = telebot.TeleBot(BOT_TOKEN)
bonus = {}

# Animation URLs or file IDs (You need to replace these with actual file IDs or URLs for the animations)
welcome_animation = "https://www.icegif.com/wp-content/uploads/2023/10/icegif-17.gif"  # Replace with actual URL or file ID
bonus_animation = "https://img1.picmix.com/output/stamp/normal/9/4/0/0/2350049_7badd.gif"  # Replace with actual URL or file ID
coin_flip_animation = "https://1b-f.s3.eu-west-1.amazonaws.com/a/146196-A15C1B6A-D5AE-41A2-9C20-912324FA259B-0-1598508964.gif"  # Replace with actual URL or file ID

def menu(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 Account')
    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')
    keyboard.row('⚙️ Set Wallet', '📊 Statistics')
    keyboard.row('🪙 Coin Tap Game')
    bot.send_message(user_id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)

def join_required(user_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("Join Bum", url="https://t.me/blum/app?startapp=ref_DWusEZ3TeD"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join OKX Racer", url="https://t.me/OKX_official_bot/OKX_Racer?startapp=linkCode_130623953"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join Kolo", url="https://t.me/kolo?start=ref_7060686316"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join NotPixel", url="https://t.me/notpixel/app?startapp=f7060686316"))
    keyboard.add(telebot.types.InlineKeyboardButton("Continue", callback_data="continue"))
    bot.send_message(user_id, "*To qualify for a reward, please join the following bots:*\n\nClick each link to join, then press Continue.", parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    # Send welcome animation
    bot.send_animation(user_id, welcome_animation)
    try:
        with open('users.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"referred": {}, "referby": {}, "balance": {}, "wallet": {}, "total": 0}

    if user_id not in data['referred']:
        data['referred'][user_id] = 0
        data['total'] += 1
    if user_id not in data['referby']:
        data['referby'][user_id] = message.text.split()[1] if len(message.text.split()) > 1 else user_id
        if data['referby'][user_id] != user_id:
            referrer = data['referby'][user_id]
            data['referred'][referrer] += 1
            data['balance'][referrer] = data['balance'].get(referrer, 0) + Per_Refer
    if user_id not in data['balance']:
        data['balance'][user_id] = 0
    if user_id not in data['wallet']:
        data['wallet'][user_id] = "none"

    with open('users.json', 'w') as file:
        json.dump(data, file)

    bot.send_message(user_id, "*Welcome to the bot!*", parse_mode="Markdown")
    join_required(user_id)

@bot.callback_query_handler(func=lambda call: call.data == "continue")
def continue_callback(call):
    user_id = call.message.chat.id
    bot.send_message(user_id, "*Thank you for joining! Accessing rewards...*", parse_mode="Markdown")
    bot.send_message(user_id, "If you have not joined, you will receive no reward.", parse_mode="Markdown")
    menu(user_id)

@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.chat.id
    user_id_str = str(user_id)
    try:
        with open('users.json', 'r') as file:
            data = json.load(file)

        if message.text == '🎁 Bonus':
            cur_time = int(time.time())
            if (user_id not in bonus.keys()) or (cur_time - bonus[user_id] > 86400):
                data['balance'][user_id_str] += Daily_bonus
                bot.send_animation(user_id, bonus_animation)  # Send bonus animation
                bot.send_message(user_id, f"Congrats! You received {Daily_bonus} tokens.")
                bonus[user_id] = cur_time
                with open('users.json', 'w') as file:
                    json.dump(data, file)
            else:
                bot.send_message(user_id, "❌ You can only claim the bonus once every 24 hours.")

        elif message.text == "🪙 Coin Tap Game":
            bot.send_animation(user_id, coin_flip_animation)  # Send coin flip animation
            bot.send_message(user_id, "Guess the outcome of the coin flip! Type 'Heads' or 'Tails'.")
            bot.register_next_step_handler(message, coin_tap_game)

    except Exception as e:
        bot.send_message(user_id, "An error occurred. Please try again later.")

def coin_tap_game(message):
    user_id_str = str(message.chat.id)
    guess = message.text.lower()
    if guess not in ['heads', 'tails']:
        bot.send_message(message.chat.id, "❌ Invalid choice. Type 'Heads' or 'Tails' to play.")
        bot.register_next_step_handler(message, coin_tap_game)
        return
    outcome = random.choice(['heads', 'tails'])
    if guess == outcome:
        with open('users.json', 'r') as file:
            data = json.load(file)
        data['balance'][user_id_str] += Game_reward
        with open('users.json', 'w') as file:
            json.dump(data, file)
        bot.send_message(message.chat.id, f"🎉 Correct! It was {outcome.capitalize()}. You win {Game_reward} tokens!")
    else:
        bot.send_message(message.chat.id, f"❌ Sorry, it was {outcome.capitalize()}. Better luck next time!")
    menu(message.chat.id)

bot.polling()
