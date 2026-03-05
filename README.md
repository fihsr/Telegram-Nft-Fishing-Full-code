# Telegram-Nft-Fishing-Full-code

# NFT Gift Scam Bot Analysis

Этот проект представляет собой Telegram-бота, замаскированного под гарант-сервис для безопасной продажи NFT-подарков, но фактически предназначенного для сбора банковских карт и имитации фиктивных сделок.

---

## 🚨 ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ 🚨

**Данный код создан ИСКЛЮЧИТЕЛЬНО для образовательных целей и анализа. Использование этого кода для мошенничества является ПРЕСТУПЛЕНИЕМ и преследуется по закону.**

---

## Анализ бота

### Что делает этот код:

1. **Маскируется под легитимный сервис**
   - Представляет себя как "бот-гарант" для безопасных сделок
   - Использует доверительную лексику ("безопасно", "гарантия", "защита")
   - Имеет разделы "Поддержка", "Инструкция", "Отзывы", "Бонусы"

2. **Создает фиктивные сделки**
   - Генерирует уникальные ID сделок
   - Создает ссылки-приглашения для "покупателей"
   - Имитирует полный цикл сделки

3. **Собирает банковские карты**
   - Запрашивает номер карты для "выплаты средств"
   - Валидирует формат (16 цифр)
   - Сохраняет в базу данных

4. **Использует психологические приемы**
   - Предлагает "скидку 10%" для покупателей
   - Предлагает "бонус +10%" для продавцов
   - Создает иллюзию выгоды и срочности

5. **Механизм обмана:**
   Вы - покупатель, Жертва - продавец
   - "Продавец" создает сделку и отправляет ссылку
   - "Покупатель" присоединяется
   - "Продавец" вводит ссылку на подарок и цену
   - "Покупатель" нажимает "Оплатить" (реальной оплаты нет)
   - "Продавец" отправляет подарок вам
   - "Покупатель" подтверждает, что подарок пришел
   - После подтверждения получения бот запрашивает карту продавца для "выплаты"
   - В итоге: у вас остается подарок, а у продавца ничего.

---

## README.md (English)

# NFT Gift Scam Bot Analysis

This project is a Telegram bot disguised as an escrow service for secure NFT gift trading, but actually designed to collect bank card numbers and simulate fake transactions.

## ⚠️ IMPORTANT WARNING ⚠️

**This code is created EXCLUSIVELY for educational purposes and analysis. Using this code for fraud is a CRIME and is prosecuted by law.**

## How it works:

1. **Disguises as legitimate service**
   - Presents itself as an "escrow bot" for secure transactions
   - Uses trust-building language ("secure", "guarantee", "protection")
   - Has "Support", "Instructions", "Reviews", "Bonuses" sections

2. **Creates fake transactions**
   - Generates unique deal IDs
   - Creates invitation links for "buyers"
   - Simulates complete transaction cycle

3. **Collects bank cards**
   - Asks for card number for "payout"
   - Validates format (16 digits)
   - Stores in database

4. **Uses psychological tricks**
   - Offers "10% discount" for buyers
   - Offers "+10% bonus" for sellers
   - Creates illusion of profit and urgency
     
5. **The Scam Mechanism:**
You are the buyer, the victim is the seller
- The "Seller" creates a deal and sends a link
- The "Buyer" joins
- The "Seller" enters the gift link and price
- The "Buyer" clicks "Pay" (no actual payment)
- The "Seller" sends the gift to you
- The "Buyer" confirms that the gift has arrived
- After confirmation of receipt, the bot requests the seller's card for "payment"
- The end result: you keep the gift, and the seller receives nothing.

---

## Технический анализ

### Структура базы данных

```sql
users:
- user_id (PRIMARY KEY)
- username
- card_number
- created_at

deals:
- deal_id (PRIMARY KEY)
- seller_id
- seller_username
- buyer_id
- buyer_username
- gift_link
- price
- status
- infected (счетчик "отправок")
- created_at

user_states:
- user_id (PRIMARY KEY)
- waiting_for_card
- waiting_for_card_payment
- created_at
```

### Статусы сделок
- `created` - создана
- `waiting_gift_info` - ожидание ссылки на подарок
- `waiting_price` - ожидание цены
- `waiting_payment` - ожидание оплаты
- `paid` - оплачено
- `gift_sent` - подарок отправлен
- `completed` - завершено

### Админ-панель
- Команда `/admpanel` доступна только ADMIN_ID
- Показывает все сделки
- Отображает количество "отправок" (infected)
- Позволяет отслеживать собранные данные

---

## Как распознать мошеннического бота

1. **Запрос банковской карты**
   - Легитимные боты НЕ запрашивают карты в чате

2. **Слишком выгодные условия**
   - Скидки 10% и бонусы без реальных транзакций

3. **Отсутствие реальной оплаты**
   - Кнопка "Оплатить" не ведет на платежный шлюз

4. **Сбор личных данных**
   - Запрос карты после "завершения" сделки

5. **Анонимность**
   - Нет информации о компании/регистрации

---

## Protection Against Such Bots

1. **NEVER share bank card details in Telegram chats**
2. **Verify bot authenticity through official sources**
3. **Check bot's username and history**
4. **Be skeptical of "too good to be true" offers**
5. **Use official marketplaces with real escrow**

---

## Юридические последствия

Создание и использование подобных ботов для мошенничества может привести к:

- Уголовной ответственности (ст. 159 УК РФ "Мошенничество")
- Блокировке аккаунтов в Telegram
- Внесению в черные списки
- Гражданским искам от пострадавших

---
