# Пример обработки различных событий

# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from dotenv import load_dotenv
import os

# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

buttons = [
    InlineKeyboardButton('RU', callback_data = 'ru'),
    InlineKeyboardButton('EN', callback_data = 'en'), 
] 

# форма inline клавиатуры
form_ver = True
if form_ver:    # если вертикальное расположение
    inline_frame = [
        [buttons[0]], [buttons[1]]
    ]
else:
    inline_frame = [
        [buttons[0], buttons[1]]
    ]   

# создаем inline клавиатуру
inline_keyboard = InlineKeyboardMarkup(inline_frame)

# функция-обработчик команды /start
async def start(update: Update, _):
   # прикрепляем inline клавиатуру к сообщению
    await update.message.reply_text('Выберите язык бота:', reply_markup=inline_keyboard)

# функция-обработчик нажатий на кнопки
async def button(update: Update, context):

    # получаем callback query из update
    query = update.callback_query
    context.user_data['lang'] = query.data

    # всплывающее уведомление
    await query.answer('Это всплывающее уведомление!')
    
    # редактируем сообщение после нажатия
    await query.edit_message_text(text = f'Вы выбрали язык: {query.data}')
    
    # новая клавиатура
    await query.message.reply_text(text = 'Выберите  язык бота:', reply_markup=inline_keyboard)


# функция-обработчик текстовых сообщений
async def text(update, context):
    lang = context.user_data.get('lang', 'ru') 
    match lang:
        case 'ru':
            await update.message.reply_text('Текстовое сообщение получено!')
        case 'en':
            await update.message.reply_text('We’ve received a message from you!')

# функция-обработчик сообщений с изображениями
async def image(update: Update, context):
    lang = context.user_data.get('lang', 'ru') 
    # сообщение от бота
    match lang:
        case 'ru':
            await update.message.reply_text('Фотография сохранена')
        case 'en':
            await update.message.reply_text('Photo saved!')

    # получаем изображение из апдейта
    quality = -1 # качество -1 - высокое, 0 - низкое
    file = await update.message.photo[quality].get_file()
    
    # сохраняем изображение на диск
    await file.download_to_drive('photos/save.jpg')

# функция-обработчик голосовых сообщений
async def voice(update, context):
    lang = context.user_data.get('lang', 'ru') 
    
    match lang:
        case 'ru':
            caption = 'Голосовое сообщение получено'
        case 'en':
            caption = 'We’ve received a voice message from you!'

    await update.message.reply_photo('media/start.jpg', caption = caption)

# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем CallbackQueryHandler (для inline кнопок)
    application.add_handler(CallbackQueryHandler(button))
    
    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # добавляем обработчик сообщений с фотографиями
    application.add_handler(MessageHandler(filters.PHOTO, image))

    # добавляем обработчик голосовых сообщений
    application.add_handler(MessageHandler(filters.VOICE, voice))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    print('Бот запущен...')    
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":      # если модуль запущен как основная программа

    # запуск бота
    main()