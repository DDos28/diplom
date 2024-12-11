import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import database
import datetime

CHOOSING_DOCTOR = 1
CHOOSING_SERVICE = 2
CHOOSING_DATE_TIME = 3
CONFIRMATION = 4

BOT_TOKEN = '7037708319:AAFaxoOelXsZx_U5h7XzSwJJpa78tgNpilE'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Список врачей", callback_data='doctors')],
        [InlineKeyboardButton("Список услуг", callback_data='services')],
        [InlineKeyboardButton("Записаться на прием", callback_data='appointment')],
        [InlineKeyboardButton("Отзывы", callback_data='reviews')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите действие:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'doctors':
        doctors = database.get_doctors()
        text = "Список врачей:\n"
        for doctor in doctors:
            text += f"- {doctor[1]} ({doctor[2]})\n"
        await query.edit_message_text(text=text)
    elif query.data == 'services':
        services = database.get_services()
        text = "Список услуг:\n"
        for service in services:
            text += f"- {service[1]} - {service[2]} руб. ({service[3]})\n"
        await query.edit_message_text(text=text)
    elif query.data == 'reviews':
        reviews = database.get_reviews()
        text = "Отзывы:\n"
        for review in reviews:
            text += f"- {review[0]} ({review[1]} звезд)\n"
        await query.edit_message_text(text=text)
    elif query.data == 'appointment':
        await query.edit_message_text(text="Функция записи на прием пока что находится в разработке.") # временная обработка

async def choose_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doctors = database.get_doctors()
    keyboard = []
    for doctor in doctors:
        keyboard.append([InlineKeyboardButton(doctor[1], callback_data=f'doctor_{doctor[0]}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите врача:", reply_markup=reply_markup)
    return CHOOSING_DOCTOR

async def doctor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    doctor_id = int(query.data.split('_')[1])
    context.user_data['doctor_id'] = doctor_id
    await query.edit_message_text(text=f"Вы выбрали врача: {query.data.split('_')[0]}. Выберите услугу.")
    services = database.get_services()
    keyboard = []
    for service in services:
      keyboard.append([InlineKeyboardButton(service[1], callback_data=f'service_{service[0]}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите услугу:", reply_markup=reply_markup)
    return CHOOSING_SERVICE


async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service_id = int(query.data.split('_')[1])
    context.user_data['service_id'] = service_id
    await query.edit_message_text(text=f"Вы выбрали услугу: {query.data.split('_')[0]}. Выберите дату и время.")
    #  Убираем return ConversationHandler.END
    return CHOOSING_DATE_TIME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Запись отменена.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def choose_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data=f'date_{today.isoformat()}')],
        [InlineKeyboardButton("Завтра", callback_data=f'date_{tomorrow.isoformat()}')]
        # Здесь можно добавить больше дней
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите дату:", reply_markup=reply_markup)
    return CHOOSING_DATE_TIME


async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    date_str = query.data.split('_')[1]
    date = datetime.date.fromisoformat(date_str)
    context.user_data['date'] = date_str
    available_slots = database.get_available_slots(context.user_data['doctor_id'], date_str)
    if available_slots:
        keyboard = []
        for slot in available_slots:
            keyboard.append([InlineKeyboardButton(slot, callback_data=f'time_{slot}')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите время:", reply_markup=reply_markup)
        return CHOOSING_DATE_TIME
    else:
        await query.edit_message_text(text="К сожалению, на эту дату нет свободных слотов.")
        return CHOOSING_DATE_TIME

async def time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    time = query.data.split('_')[1]
    context.user_data['time'] = time
    datetime_str = f"{context.user_data['date']} {time}"
    await query.edit_message_text(text=f"Вы выбрали время: {time}. Подтвердить запись?")
    keyboard = [[InlineKeyboardButton("Подтвердить", callback_data='confirm'), InlineKeyboardButton("Отмена", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Подтвердить запись?", reply_markup=reply_markup)
    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'confirm':
        success = database.book_appointment(update.effective_user.id, context.user_data['doctor_id'], context.user_data['service_id'], f"{context.user_data['date']} {context.user_data['time']}")
        if success:
            await query.edit_message_text(text="Запись успешно создана!")
        else:
            await query.edit_message_text(text="Ошибка при создании записи. Попробуйте еще раз.")
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(choose_doctor, pattern='^appointment$')],
        states={
            CHOOSING_DOCTOR: [CallbackQueryHandler(doctor_selected, pattern='^doctor_')],
            CHOOSING_SERVICE: [CallbackQueryHandler(service_selected, pattern='^service_')],
            CHOOSING_DATE_TIME: [CallbackQueryHandler(choose_datetime, pattern='^service_'),
                                 # Добавлен этот обработчик
                                 CallbackQueryHandler(date_selected, pattern='^date_'),
                                 CallbackQueryHandler(time_selected, pattern='^time_')],
            CONFIRMATION: [CallbackQueryHandler(confirmation, pattern='^confirm$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    button_handler = CallbackQueryHandler(button_handler)
    application.add_handler(button_handler)

    application.run_polling()