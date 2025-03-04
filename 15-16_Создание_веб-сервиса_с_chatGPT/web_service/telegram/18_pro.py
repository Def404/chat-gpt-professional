# Пример синхронного обращения к API

# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import requests
from collections import deque


# загружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# функция-обработчик команды /start
async def start(update, context):

    # установка счетчика запросов
    context.user_data['count'] = 15

    user_id = update.message.from_user.id
    context.bot_data[user_id] = {}
    context.bot_data[user_id]['history'] = ''

    # сообщение пользователю
    await update.message.reply_text('Привет! Это пример синхронного обращения к API')

# функция-обработчик команды /status
async def status(update, context):
    
    # сообщение пользователю
    await update.message.reply_text(f'Осталось запросов: {context.user_data["count"]}')


# функция-обработчик текстовых сообщений
async def text(update, context):
    user_id = update.message.from_user.id
    
    if context.user_data.get('count', 0) == 0:
        await update.message.reply_text('Лимит запросов исчерпан!')
        return

    # Уменьшаем счетчик запросов
    context.user_data['count'] -= 1

    # Инициализируем очередь для хранения последних 5 вопросов
    if 'history' not in context.bot_data.get(user_id, {}):
        context.bot_data[user_id] = {'history': deque(maxlen=5)}  # Храним только вопросы

    # Добавляем новый вопрос пользователя
    context.bot_data[user_id]['history'].append(update.message.text)

    # Формируем запрос к API (только последние 5 вопросов)
    conversation_history = "\n".join(context.bot_data[user_id]['history'])
    answer = await query_api(conversation_history)

    # Ответ пользователю
    print(f'answer: {answer}')
    await update.message.reply_text(answer)

# Функция для запроса к API
async def query_api(history):
    text = f'''
    Ты консультант, и тебе поступил вопрос от клиента. Вот ваш диалог с ним: {history}
'''
    param = {
        'text': text
    }    
    response = requests.post('http://127.0.0.1:8000/answer', json = param)
    answer = response.json()

    return answer['message']

# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик команды /status
    application.add_handler(CommandHandler("status", status))

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