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

# Animation URLs or file IDs (Replace with actual file IDs or URLs)
welcome_animation = "WELCOME_ANIMATION_URL"
bonus_animation = "BONUS_ANIMATION_URL"
coin_flip_animation = "COIN_FLIP_ANIMATION_URL"

# Main menu
def menu(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 Account')
    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')
    keyboard.row('⚙️ Set Wallet', '📊 Statistics')
    keyboard.row('🪙 Coin Tap Game')
    bot.send_message(user_id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)

# Join required message
def join_required(user_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("Join Bum", url="https://t.me/blum/app?startapp=ref_DWusEZ3TeD"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join OKX Racer", url="https://t.me/OKX_official_bot/OKX_Racer?startapp=linkCode_130623953"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join Kolo", url="https://t.me/kolo?start=ref_7060686316"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join NotPixel", url="https://t.me/notpixel/app?startapp=f7060686316"))
    keyboard.add(telebot.types.InlineKeyboardButton("Continue", callback_data="continue"))
    bot.send_message(user_id, "*To qualify for rewards, join the following bots:*", parse_mode="Markdown", reply_markup=keyboard)

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
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
        referrer = message.text.split()[1] if len(message.text.split()) > 1 else user_id
        data['referby'][user_id] = referrer
        if referrer != user_id:
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

# Continue callback for join confirmation
@bot.callback_query_handler(func=lambda call: call.data == "continue")
def continue_callback(call):
    user_id = call.message.chat.id
    bot.send_message(user_id, "*Thank you for joining!* Accessing rewards...", parse_mode="Markdown")
    menu(user_id)

# Handler for menu buttons
@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.chat.id
    user_id_str = str(user_id)
    try:
        with open('users.json', 'r') as file:
            data = json.load(file)

        if message.text == '🎁 Bonus':
            handle_bonus(user_id, data, user_id_str)

        elif message.text == "🪙 Coin Tap Game":
            bot.send_animation(user_id, coin_flip_animation)
            bot.send_message(user_id, "Guess the outcome of the coin flip! Type 'Heads' or 'Tails'.")
            bot.register_next_step_handler(message, coin_tap_game)

        elif message.text == "🆔 Account":
            bot.send_message(user_id, f"Your balance: {data['balance'].get(user_id_str, 0)} tokens")

        elif message.text == "🙌🏻 Referrals":
            referrals = data['referred'].get(user_id_str, 0)
            bot.send_message(user_id, f"Referrals: {referrals} | Earnings: {referrals * Per_Refer} tokens")

        elif message.text == "⚙️ Set Wallet":
            bot.send_message(user_id, "Please enter your wallet address:")
            bot.register_next_step_handler(message, set_wallet, data)

        elif message.text == "📊 Statistics":
            bot.send_message(user_id, f"Total users: {data['total']}")

        elif message.text == "💸 Withdraw":
            balance = data['balance'].get(user_id_str, 0)
            if balance >= Mini_Withdraw:
                bot.send_message(user_id, "Withdrawal successful!")
                data['balance'][user_id_str] = 0
                with open('users.json', 'w') as file:
                    json.dump(data, file)
            else:
                bot.send_message(user_id, f"You need at least {Mini_Withdraw} tokens to withdraw.")

    except Exception as e:
        bot.send_message(user_id, "An error occurred. Please try again later.")

# Helper function for bonus
def handle_bonus(user_id, data, user_id_str):
    cur_time = int(time.time())
    if (user_id not in bonus.keys()) or (cur_time - bonus[user_id] > 86400):
        data['balance'][user_id_str] += Daily_bonus
        bot.send_animation(user_id, bonus_animation)
        bot.send_message(user_id, f"Congrats! You received {Daily_bonus} tokens.")
        bonus[user_id] = cur_time
        with open('users.json', 'w') as file:
            json.dump(data, file)
    else:
        bot.send_message(user_id, "❌ You can only claim the bonus once every 24 hours.")

# Coin tap game function
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

# Set wallet function
def set_wallet(message, data):
    user_id = str(message.chat.id)
    wallet_address = message.text
    data['wallet'][user_id] = wallet_address
    with open('users.json', 'w') as file:
        json.dump(data, file)
    bot.send_message(message.chat.id, f"Wallet address set to: {wallet_address}")

bot.polling()
