# Пример обработки различных событий

# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# функция-обработчик команды /start
async def start(update, context):
    await update.message.reply_text("Добро пожаловать, мой дорогой друг!")

# функция-обработчик команды /help
async def help(update, context):
    message = '''
        Этот под предназначен для обучения!❗
    '''
    await update.message.reply_text(message)

# функция-обработчик текстовых сообщений
async def text(update, context):
    await update.message.reply_text('Текст, текст, текст…')


# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик команды /help
    application.add_handler(CommandHandler("help", help))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    print('Бот запущен...')    
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":      # если модуль запущен как основная программа

    # запуск бота
    main()