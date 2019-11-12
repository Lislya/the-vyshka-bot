from functools import wraps

import bs4
import requests
from telegram import ChatAction, ParseMode, InputMediaPhoto

import keyboards


def send_action(action):
    """ Создает у пользователя видимость, что бот 'печатает' """

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


def start(update, context):
    """" Вывод меню на клавиатуру пользователя """
    start_keyboard = keyboards.START_KEYBOARD()
    start_message = 'Выберите пункт меню:'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=start_message,
                             reply_markup=start_keyboard)


def text(update, context):
    """" Обработка текстовых команд """

    command = update.message.text
    if command == 'Новости':
        news(update, context)
    elif command == 'Люди':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='хуюди')
    elif command == 'Тренды':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='хуенды')
    elif command == 'Мнения':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='хуения')
    elif command == 'Места':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='нет мест, пройдите в вагон')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='???????')


def callback(update, context):
    """" Функия "реагирования" на нажатия inline-кнопки """
    button_data = update.callback_query.data
    change_article(update, context, button_data)


# Все новости, полученные с сайта (с первой страницы)
articles = {}
# Текущий индекс показываемой новости
CURRENT_ARTICLE_INDEX = 0


@send_action(ChatAction.TYPING)
def news(update, context):
    """" Получаем список новостей с сайта The Vyshka с помощью библиотеки BeautifulSoup """

    req = requests.get('https://thevyshka.ru/cat/novosti/')  # посылаем запрос
    soup = bs4.BeautifulSoup(req.text, 'html.parser')        # парсим полученный с сайта текст
    articles_imgs = soup.select('article  img')              # выбираем список всех картинок
    articles_titles = soup.select('.article__title')         # выбираем список все названия новостей
    articles_link = soup.select('.article__title a')         # выбираем все ссылки на новости
    articles_content = soup.select('.article__content')      # выбираем тексты статей

    for i in range(len(articles_titles)):                    # пробегаемся по нашему списку новостей,
        title = articles_titles[i].getText()[1:]             # который выглядит примерно вот так:
        content = articles_content[i].getText()              # [новость 1, новость2, новость3, ...]
        link = 'https:/' + articles_link[i]['href'][1:]      # и складываем их в "словарик" следующего вида
        image = 'https:/' + articles_imgs[i]['src'][1:]      # {новость: картинка, и т. д.} в переменную articles

        message = title + content + '\n' + link
        articles[message] = image

    # посылаем первую новость пользователю
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=articles[list(articles.keys())[0]],
                           caption=list(articles.keys())[0],
                           reply_markup=keyboards.NEWS_INLINE_KEYBOARD())


def change_article(update, context, prev_or_next):
    """" Сменяем новость в показываемом сообщении в зависимости от нажатой кнопки """
    global CURRENT_ARTICLE_INDEX
    if prev_or_next == 'next':
        CURRENT_ARTICLE_INDEX = CURRENT_ARTICLE_INDEX + 1 if CURRENT_ARTICLE_INDEX < len(list(articles)) - 1 else 0
    elif prev_or_next == 'prev':
        CURRENT_ARTICLE_INDEX -= 1

    photo_link = articles[list(articles.keys())[CURRENT_ARTICLE_INDEX]]
    caption = list(articles.keys())[CURRENT_ARTICLE_INDEX]
    media = InputMediaPhoto(media=photo_link,
                            caption=caption)
    context.bot.edit_message_media(chat_id=update.effective_chat.id,
                                   message_id=update.effective_message.message_id,
                                   media=media,
                                   reply_markup=keyboards.NEWS_INLINE_KEYBOARD())


@send_action(ChatAction.TYPING)
def about(update, context):
    """" команда about: выводит список доступных команд """
    message = 'Привет! Я бот The Vyshka. Вот какие команды я знаю:\n'
    message += '/start - начало работы\n'
    message += '/about - обо мне\n'
    message += '/news - последние новости\n'
    message += '/people - люди на The Vyshka\n'
    message += '/trends - тренды\n'
    message += '/opinions - интересные мнения\n'
    message += '/places - интересные места\n'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message)


def unknown(update, context):
    """ Реагирует на неизвестную команду (команда начинается с /) """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Извини, не знаю такой команды.")
