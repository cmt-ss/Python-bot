import time
import json
import telebot

# TOKEN DETAILS
BOT_TOKEN = "7462875981:AAGmUrEzKk75j7XjuPSVuAGiT2_drDdLv_0"
Daily_bonus = 1  # Daily bonus amount
Mini_Withdraw = 0.5  # Minimum withdrawal amount
Per_Refer = 0.0001  # Referral bonus amount

bot = telebot.TeleBot(BOT_TOKEN)
bonus = {}

def menu(id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 Account')
    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')
    keyboard.row('⚙️ Set Wallet', '📊 Statistics')
    bot.send_message(id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user = message.chat.id
        user = str(user)
        data = json.load(open('users.json', 'r'))
        if user not in data['referred']:
            data['referred'][user] = 0
            data['total'] = data['total'] + 1
        if user not in data['referby']:
            data['referby'][user] = user
        if user not in data['balance']:
            data['balance'][user] = 0
        if user not in data['wallet']:
            data['wallet'][user] = "none"
        json.dump(data, open('users.json', 'w'))
        bot.send_message(user, "*Welcome to the bot!*", parse_mode="Markdown")
        menu(user)
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred. Please try again later.")

@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        user_id = message.chat.id
        user = str(user_id)
        data = json.load(open('users.json', 'r'))

        if message.text == '🆔 Account':
            accmsg = '*👮 User: {}\n⚙️ Wallet: `{}`\n💸 Balance: `{}`*'
            wallet = data['wallet'].get(user, "none")
            balance = data['balance'].get(user, 0)
            msg = accmsg.format(message.from_user.first_name, wallet, balance)
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == '🙌🏻 Referrals':
            ref_msg = "*⏯️ Total Invites: {} Users\n\n🔗 Referral Link: {}*"
            ref_count = data['referred'].get(user, 0)
            bot_name = bot.get_me().username
            ref_link = f'https://telegram.me/{bot_name}?start={user_id}'
            msg = ref_msg.format(ref_count, ref_link)
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == '🎁 Bonus':
            cur_time = int(time.time())
            if (user_id not in bonus.keys()) or (cur_time - bonus[user_id] > 86400):
                data['balance'][user] += Daily_bonus
                bot.send_message(user_id, f"Congrats! You received {Daily_bonus} tokens.")
                bonus[user_id] = cur_time
                json.dump(data, open('users.json', 'w'))
            else:
                bot.send_message(user_id, "❌ You can only claim the bonus once every 24 hours.")

        elif message.text == '⚙️ Set Wallet':
            keyboard = telebot.types.ReplyKeyboardMarkup(True)
            keyboard.row('🚫 Cancel')
            send = bot.send_message(user_id, "_⚠️ Send your TRX wallet address._", parse_mode="Markdown", reply_markup=keyboard)
            bot.register_next_step_handler(send, trx_address)

        elif message.text == "📊 Statistics":
            msg = "*📊 Total members: {} Users*".format(data['total'])
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == "💸 Withdraw":
            balance = data['balance'].get(user, 0)
            wallet = data['wallet'].get(user, "none")
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
    try:
        if message.text == "🚫 Cancel":
            return menu(message.chat.id)
        elif len(message.text) == 34:  # Example check for wallet address length
            user_id = str(message.chat.id)
            data = json.load(open('users.json', 'r'))
            data['wallet'][user_id] = message.text
            json.dump(data, open('users.json', 'w'))
            bot.send_message(message.chat.id, "✅ Wallet address set successfully.")
            menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, "❌ Invalid wallet address.")
            menu(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred. Please try again later.")

def amo_with(message):
    try:
        amount = float(message.text)
        user_id = str(message.chat.id)
        data = json.load(open('users.json', 'r'))
        balance = data['balance'].get(user_id, 0)
        
        if amount <= balance and amount >= Mini_Withdraw:
            data['balance'][user_id] -= amount
            json.dump(data, open('users.json', 'w'))
            bot.send_message(message.chat.id, f"✅ Withdrawal of {amount} tokens initiated.")
        else:
            bot.send_message(message.chat.id, f"❌ Invalid amount. Minimum withdrawal is {Mini_Withdraw} tokens.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Please enter a valid amount.")
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred. Please try again later.")

bot.polling()
