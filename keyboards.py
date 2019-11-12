from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

"""" Это клавиатуры, которые используются в данном боте """


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def START_KEYBOARD():
    button_list = [['Новости'],
                   ['Тренды', 'Люди'],
                   ['Мнения', 'Места']]
    return ReplyKeyboardMarkup(button_list, resize_keyboard=True)


def NEWS_INLINE_KEYBOARD():
    button_list = [InlineKeyboardButton('<===', callback_data='prev'),
                   InlineKeyboardButton('===>', callback_data='next')]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
