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
        people(update, context)
    elif command == 'Тренды':
        trends(update, context)
    elif command == 'Мнения':
        views(update, context)
    elif command == 'Места':
        places(update, context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Извини, не знаю такой команды.')


# Все новости, полученные с сайта (с первой страницы)
articles_dict = []
people_dict = []
trends_dict = []
views_dict = []
places_dict = []
# Текущий индекс показываемой новости
CURRENT_ARTICLE_INDEX = 0
CURRENT_PEOPLE_INDEX = 0
CURRENT_TRENDS_INDEX = 0
CURRENT_VIEWS_INDEX = 0
CURRENT_PLACES_INDEX = 0


def callback(update, context):
    """" Функия "реагирования" на нажатия inline-кнопки """
    global CURRENT_ARTICLE_INDEX
    global CURRENT_PEOPLE_INDEX
    global CURRENT_TRENDS_INDEX
    global CURRENT_VIEWS_INDEX
    global CURRENT_PLACES_INDEX
    button_data = update.callback_query.data
    category = update.effective_message.caption
    if 'novosti' in category:
        CURRENT_ARTICLE_INDEX = change_article(update, context, button_data, CURRENT_ARTICLE_INDEX, articles_dict)
    elif 'people' in category:
        CURRENT_PEOPLE_INDEX = change_article(update, context, button_data, CURRENT_PEOPLE_INDEX, people_dict)
    elif 'trends' in category:
        CURRENT_TRENDS_INDEX = change_article(update, context, button_data, CURRENT_TRENDS_INDEX, trends_dict)
    elif 'views' in category:
        CURRENT_VIEWS_INDEX = change_article(update, context, button_data, CURRENT_VIEWS_INDEX, views_dict)
    elif 'places' in category:
        CURRENT_PLACES_INDEX = change_article(update, context, button_data, CURRENT_PLACES_INDEX, places_dict)


@send_action(ChatAction.TYPING)
def news(update, context):
    get_content(update, context, 'novosti', articles_dict)


@send_action(ChatAction.TYPING)
def people(update, context):
    get_content(update, context, 'people', people_dict)


@send_action(ChatAction.TYPING)
def trends(update, context):
    get_content(update, context, 'trends', trends_dict)


@send_action(ChatAction.TYPING)
def views(update, context):
    get_content(update, context, 'views', views_dict)


@send_action(ChatAction.TYPING)
def places(update, context):
    get_content(update, context, 'places', places_dict)


def get_content(update, context, category, content_collection):
    req = requests.get('https://thevyshka.ru/cat/' + category)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    images = soup.select('article  img')
    dates = soup.select('.article__meta-links li')
    titles = soup.select('.article__title')
    links = soup.select('.article__title a')
    contents = soup.select('.article__content')

    for i in range(len(titles)):
        title = titles[i].getText()[1:]
        date = dates[i].getText()
        content = contents[i].getText()
        link = 'https:/' + links[i]['href'][1:]
        image = 'https:/' + images[i]['src'][1:]
        message = title + content + '\n' + date + '\n' + '#' + category

        news_token = {link: {image: message}}
        content_collection.append(news_token)

    first_news_link = list(content_collection[0].keys())[0]
    first_photo = list(list(content_collection[0].values())[0])[0]
    first_caption = list(content_collection[0].values())[0][first_photo]
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=first_photo,
                           caption=first_caption,
                           reply_markup=keyboards.NEWS_INLINE_KEYBOARD(first_news_link))


def change_article(update, context, prev_or_next, index, content_collection):
    """" Сменяем новость в показываемом сообщении в зависимости от нажатой кнопки """
    if prev_or_next == 'next':
        index = index + 1 if index < len(list(content_collection)) - 1 else 0
    elif prev_or_next == 'prev':
        index -= 1

    news_link = list(content_collection[index].keys())[0]
    photo_link = list(list(content_collection[index].values())[0])[0]
    caption = list(content_collection[index].values())[0][photo_link]
    media = InputMediaPhoto(media=photo_link,
                            caption=caption)
    context.bot.edit_message_media(chat_id=update.effective_chat.id,
                                   message_id=update.effective_message.message_id,
                                   media=media,
                                   reply_markup=keyboards.NEWS_INLINE_KEYBOARD(news_link))
    return index


@send_action(ChatAction.TYPING)
def about(update, context):
    """" команда about: выводит список доступных команд """

    message = 'Привет! Я бот The Vyshka. Помогу тебе быть в курсе последних событий ВШЭ:\n'
    message += '/start - начало работы\n'
    message += '/about - обо мне\n'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message)


def unknown(update, context):
    """ Реагирует на неизвестную команду (команда начинается с /) """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Извини, не знаю такой команды.")
