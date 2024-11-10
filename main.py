import time
import json
import telebot

# TOKEN DETAILS
BOT_TOKEN = "7462875981:AAGmUrEzKk75j7XjuPSVuAGiT2_drDdLv_0"  # Replace with your actual bot token
Daily_bonus = 1  # Daily bonus amount
Mini_Withdraw = 1  # Minimum withdrawal amount
Per_Refer = 0.5  # Referral bonus amount

bot = telebot.TeleBot(BOT_TOKEN)
bonus = {}

def menu(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 Account')
    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')
    keyboard.row('⚙️ Set Wallet', '📊 Statistics')
    bot.send_message(user_id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)

def join_required(user_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("Join Banana", url="https://t.me/OfficialBananaBot/banana?startapp=referral=CF1JDI6"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join OKX Racer", url="https://t.me/OKX_official_bot/OKX_Racer?startapp=linkCode_130623953"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join Kolo", url="https://t.me/kolo?start=ref_7060686316"))
    keyboard.add(telebot.types.InlineKeyboardButton("Join NotPixel", url="https://t.me/notpixel/app?startapp=f7060686316"))
    keyboard.add(telebot.types.InlineKeyboardButton("Continue", callback_data="continue"))
    bot.send_message(user_id, "*To qualify for a reward, please join the following bots:*\n\nClick each link to join, then press Continue.", parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
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

        if message.text == '🆔 Account':
            wallet = data['wallet'].get(user_id_str, "none")
            balance = data['balance'].get(user_id_str, 0)
            msg = f'*👮 User: {message.from_user.first_name}\n⚙️ Wallet: `{wallet}`\n💸 Balance: `{balance}`*'
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == '🙌🏻 Referrals':
            ref_count = data['referred'].get(user_id_str, 0)
            bot_name = bot.get_me().username
            ref_link = f'https://telegram.me/{bot_name}?start={user_id}'
            msg = f"*⏯️ Total Invites: {ref_count} Users\nNeed 1 referral to withdraw\n\n🔗 Referral Link: {ref_link}*"
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == '🎁 Bonus':
            cur_time = int(time.time())
            if (user_id not in bonus.keys()) or (cur_time - bonus[user_id] > 86400):
                data['balance'][user_id_str] += Daily_bonus
                bot.send_message(user_id, f"Congrats! You received {Daily_bonus} tokens. Need 1 referral to withdraw.")
                bonus[user_id] = cur_time
                with open('users.json', 'w') as file:
                    json.dump(data, file)
            else:
                bot.send_message(user_id, "❌ You can only claim the bonus once every 24 hours.")

        elif message.text == '⚙️ Set Wallet':
            keyboard = telebot.types.ReplyKeyboardMarkup(True)
            keyboard.row('🚫 Cancel')
            send = bot.send_message(user_id, "_⚠️ Send your TRX wallet address._", parse_mode="Markdown", reply_markup=keyboard)
            bot.register_next_step_handler(send, trx_address)

        elif message.text == "📊 Statistics":
            msg = f"*📊 Total members: {data['total']} Users*"
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == "💸 Withdraw":
            balance = data['balance'].get(user_id_str, 0)
            wallet = data['wallet'].get(user_id_str, "none")
            if wallet == "none":
                bot.send_message(user_id, "_❌ Wallet not set._", parse_mode="Markdown")
            elif balance >= Mini_Withdraw:
                bot.send_message(user_id, "_Enter the amount to withdraw._", parse_mode="Markdown")
                bot.register_next_step_handler(message, amo_with)
            else:
                bot.send_message(user_id, f"_❌ Your balance is too low. Minimum withdrawal is {Mini_Withdraw} tokens._", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(user_id, "An error occurred. Please try again later.")

def trx_address(message):
    user_id_str = str(message.chat.id)
    if message.text == "🚫 Cancel":
        return menu(message.chat.id)
    elif len(message.text) == 34:
        with open('users.json', 'r') as file:
            data = json.load(file)
        data['wallet'][user_id_str] = message.text
        with open('users.json', 'w') as file:
            json.dump(data, file)
        bot.send_message(message.chat.id, "✅ Wallet address set successfully.")
        menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "❌ Invalid wallet address.")
        menu(message.chat.id)

def amo_with(message):
    try:
        amount = float(message.text)
        user_id_str = str(message.chat.id)
        with open('users.json', 'r') as file:
            data = json.load(file)
        balance = data['balance'].get(user_id_str, 0)
        
        if Mini_Withdraw <= amount <= balance:
            data['balance'][user_id_str] -= amount
            with open('users.json', 'w') as file:
                json.dump(data, file)
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("Claim 100 Flying Paisa", url="https://www.mintme.com/token/Flying-Paisa/airdrop"))
            bot.send_message(
                message.chat.id,
                f"✅ Withdrawal of {amount} tokens initiated. You will receive if the Flying Paisa Coin is launched in the coming days.",
                reply_markup=keyboard
            )
        else:
            bot.send_message(message.chat.id, f"❌ Invalid amount. Minimum withdrawal is {Mini_Withdraw} tokens.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Please enter a valid amount.")
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred. Please try again later.")

bot.polling()
