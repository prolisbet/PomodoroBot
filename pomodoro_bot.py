import telebot
from telebot import types
import datetime
from datetime import timedelta
import time
import threading
import pytz
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

stop_loop = {}
work = 0
rest = 0


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, text='Привет! Я чат-бот, который поможет тебе организовать рабочий процесс! \n'
                                           'Скорее вводи команду /work и мы начнем работу.')


@bot.message_handler(commands=['work'])
def work_message(message):
    chat_id = message.chat.id
    stop_loop[chat_id] = False

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="1", callback_data='1')
    btn2 = types.InlineKeyboardButton(text="2", callback_data='2')
    btn3 = types.InlineKeyboardButton(text="3", callback_data='3')
    # Добавляем кнопки в клавиатуру
    markup.add(btn1,btn2,btn3)
    # Отправляем сообщение пользователю с этой клавиатурой
    bot.send_message(message.chat.id, '*Выбери один из трех помидоров для работы:* \n'
                                      '1. 12 минут работы - 3 минуты отдыха; \n'
                                      '2. 25 минут работы - 5 минут отдыха; \n'
                                      '3. 45 минут работы - 15 минут отдыха.',
                     parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global work, rest
    bot.answer_callback_query(callback_query_id=call.id)
    answer = ''
    if call.data == '1':
        answer = 'Вы выбрали 12 минут работы - 3 минуты отдыха'
        work = 12
        rest = 3
    elif call.data == '2':
        answer = 'Вы выбрали 25 минут работы - 5 минут отдыха'
        work = 25
        rest = 5
    elif call.data == '3':
        answer = 'Вы выбрали 45 минут работы - 15 минут отдыха'
        work = 45
        rest = 15

    bot.send_message(call.message.chat.id, answer)

    work_thread = threading.Thread(target=pomodoro_clock, args=(call.message.chat.id, work, rest))
    work_thread.start()


def pomodoro_clock(chat_id, work, rest):
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now().astimezone(moscow_tz)
    text_now = now.strftime('%H:%M')
    bot.send_message(chat_id, f'Начинаем работать в {text_now}')
    n = 0
    while True:
      work_delta = timedelta(minutes = (work+rest) * n + work)
      rest_time = (now + work_delta).strftime('%H:%M')
      rest_delta = timedelta(minutes = (work+rest) * n + (work+rest))
      work_time = (now + rest_delta).strftime('%H:%M')
      new_now = datetime.datetime.now().astimezone(moscow_tz
                                                  ).strftime('%H:%M')
      if new_now == rest_time:
          bot.send_message(chat_id, f'{rest_time} - хватит работать! Время отдыхать.')
          custom_sleep(chat_id, 60)
      elif new_now == work_time:
          bot.send_message(chat_id, f'{work_time} - хватит отдыхать! Время работать.')
          n += 1
          custom_sleep(chat_id, 60)
      if stop_loop.get(chat_id):
          break


def custom_sleep(chat_id, sec):
    start = time.time()
    while time.time() - start < sec:
        if stop_loop.get(chat_id):
            break
        pass  # Активное ожидание


@bot.message_handler(commands=['info'])
def info_message(message):
    info_text = ('«Метод помидора» (итал. tunica del pomodoro) — техника управления временем, '
                 'предложенная Франческо Чирилло в конце 1980-х. Методика предполагает увеличение '
                 'эффективности работы при меньших временных затратах за счёт глубокой концентрации '
                 'и коротких перерывов. В классической технике отрезки времени — «помидоры» длятся полчаса: '
                 '25 минут работы и 5 минут отдыха.')
    bot.reply_to(message, f'*Что же это за помидоры?* \n {info_text}', parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = ('Привет! Я чат-бот, который поможет тебе организовать рабочий процесс! \n'
                 'Вот что я умею:  \n'
                 '/start - начать общение \n'
                 '/help - показать эту справку \n'
                 '/info - узнать больше о помидорах \n'
                 '/work - начать рабочий процесс \n'
                 '/stop - остановить рабочий процесс')
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['stop'])
def stop_loop_handler(message):
    chat_id = message.chat.id
    # Остановить цикл для данного пользователя
    stop_loop[chat_id] = True
    bot.send_message(chat_id, "Поработали достаточно.")


bot.polling(none_stop=True)
