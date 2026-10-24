import telebot
from telebot import types

# Your working token
TOKEN = "8918941999:AAEkm5xAHK6eFg4wOk2ZYptTYc8o2Cl8HO4"
bot = telebot.TeleBot(TOKEN)

# IMPORTANT: Replace 123456789 with your real Telegram ID to get booking notifications!
MY_ID = 123456789

bot.remove_webhook()


# Function to create the main menu
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_about = types.KeyboardButton("ℹ️ About Stylist")
    btn_prices = types.KeyboardButton("💰 Services & Prices")
    btn_location = types.KeyboardButton("📍 Location & Hours")
    btn_book = types.KeyboardButton("📅 Book an Appointment")
    markup.add(btn_about, btn_prices, btn_location, btn_book)
    return markup


# --- Step 1: Welcome Message & Main Menu ---
@bot.message_handler(commands=["start"])
def welcome(message):
    welcome_text = (
        f"👋 Hello, {message.from_user.first_name}!\n\n"
        "Welcome to **Luxury Hair Studio** bot. ✂️\n"
        "Here you can check my services, find the salon location, and book your appointment online!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# --- Step 2: Main Menu Buttons Handling ---
@bot.message_handler(content_types=["text"])
def handle_buttons(message):
    if message.text == "ℹ️ About Stylist":
        about_text = (
            "🙋‍♂️ *About Me*\n\n"
            "Hi! My name is Alex. I am a certified top-stylist and barber with 5+ years of experience.\n"
            "I specialize in modern male & female haircuts, advanced hair coloring, and beard grooming.\n\n"
            "✨ *My Goal:* To make you look confident and feel amazing!"
        )
        bot.send_message(message.chat.id, about_text, parse_mode="Markdown")

    elif message.text == "💰 Services & Prices":
        prices_text = (
            "💰 *Our Services & Rates*\n\n"
            "• Men's Haircut + Styling — \$30\n"
            "• Women's Haircut + Blow Dry — \$45\n"
            "• Beard Trim & Shave — \$20\n"
            "• Hair Coloring / Highlights — from \$70\n\n"
            "⏳ *Duration:* Every session takes about 45-60 minutes."
        )
        bot.send_message(message.chat.id, prices_text, parse_mode="Markdown")

    elif message.text == "📍 Location & Hours":
        location_text = (
            "📍 *Our Salon Address*\n"
            "123 Beauty Street, Downtown (Next to Central Park)\n\n"
            "🕒 *Working Hours*\n"
            "• Monday - Friday: 09:00 AM - 08:00 PM\n"
            "• Saturday: 10:00 AM - 06:00 PM\n"
            "• Sunday: Closed\n\n"
            "📞 *Phone:* +1 (555) 019-2834"
        )
        bot.send_message(message.chat.id, location_text, parse_mode="Markdown")

    # --- START OF BOOKING FLOW ---
    elif message.text == "📅 Book an Appointment":
        markup_services = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_1 = types.KeyboardButton("Men's Haircut")
        btn_2 = types.KeyboardButton("Women's Haircut")
        btn_3 = types.KeyboardButton("Beard Trim")
        btn_4 = types.KeyboardButton("Hair Coloring")
        markup_services.add(btn_1, btn_2, btn_3, btn_4)

        msg = bot.send_message(
            message.chat.id,
            "Step 1/3: What service would you like to book?",
            reply_markup=markup_services,
        )
        bot.register_next_step_handler(msg, process_service_step)


# --- Step 3: Get Service -> Ask for Date & Time ---
def process_service_step(message):
    service = message.text

    if service == "/start":
        welcome(message)
        return

    # Temporary simple menu for date/time selection (user can also type custom time)
    markup_time = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_today = types.KeyboardButton("Today (ASAP)")
    btn_tomorrow_morning = types.KeyboardButton("Tomorrow Morning")
    btn_tomorrow_evening = types.KeyboardButton("Tomorrow Evening")
    markup_time.add(btn_today, btn_tomorrow_morning, btn_tomorrow_evening)

    msg = bot.send_message(
        message.chat.id,
        f"You selected: *{service}*\n\nStep 2/3: Please choose or type your preferred Date and Time (e.g., 'Tomorrow at 3 PM'):",
        reply_markup=markup_time,
        parse_mode="Markdown"
    )
    # Pass `service` data to the next step
    bot.register_next_step_handler(msg, process_time_step, service)


# --- Step 4: Get Date/Time -> Ask for Phone Number ---
def process_time_step(message, service):
    booking_time = message.text

    if booking_time == "/start":
        welcome(message)
        return

    # Request phone number using Telegram's secure contact button
    markup_phone = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_phone = types.KeyboardButton("📱 Share my Phone Number", request_contact=True)
    markup_phone.add(btn_phone)

    msg = bot.send_message(
        message.chat.id,
        "Step 3/3: Click the button below to share your phone number so I can confirm your booking:",
        reply_markup=markup_phone
    )
    # Pass `service` and `booking_time` forward
    bot.register_next_step_handler(msg, process_final_step, service, booking_time)


# --- Step 5: Final Step -> Send confirmation to client & details to Admin ---
def process_final_step(message, service, booking_time):
    # Check if user clicked the "Share Contact" button or typed it manually
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    if phone_number == "/start":
        welcome(message)
        return

    # Thank the client and return to Main Menu
    bot.send_message(
        message.chat.id,
        "🎉 *Thank you!* Your booking request has been sent successfully. I will text or call you shortly to confirm!",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

    # Format the notification for you (the Barber/Admin)
    username = f"@{message.from_user.username}" if message.from_user.username else "Hidden"
    client_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}"

    notification_text = (
        f"💇‍♂️ 🔥 **NEW BOOKING REQUEST!** 🔥\n\n"
        f"👤 *Client Name:* {client_name}\n"
        f"📱 *Telegram Username:* {username}\n"
        f"📞 *Phone:* {phone_number}\n\n"
        f"✂️ *Service:* {service}\n"
        f"📅 *Desired Time:* {booking_time}"
    )

    # Send notification to your personal Telegram ID
    try:
        bot.send_message(MY_ID, notification_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending booking notification to admin: {e}")


# Start polling
if __name__ == "__main__":
    print("Barber/Doctor Business Card Bot successfully started!")
    bot.infinity_polling()
