import logging

from telegram.ext import CommandHandler
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler

import commands

# Настраиваем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Получаем объект-"уведомитель", передав в него наш токен бота полученного от @BotFather
updater = Updater(token='719881156:AAGwXlkJ4qZDv6e49sruZqnvrFoEW0_6fuw', use_context=True)
dispatcher = updater.dispatcher


# Обработчик команды /start
start_handler = CommandHandler('start', commands.start)
dispatcher.add_handler(start_handler)

# Обработчик команды /about
about_handler = CommandHandler('about', commands.about)
dispatcher.add_handler(about_handler)


# Обработчик команды текстовых сообщений
text_command_handler = MessageHandler(Filters.text, commands.text)
dispatcher.add_handler(text_command_handler)

# Обработчик "inline"-кнопок в сообщениях
next_article_handler = CallbackQueryHandler(commands.callback)
dispatcher.add_handler(next_article_handler)

# Обработчик неизвестных команд
unknown_handler = MessageHandler(Filters.command, commands.unknown)
dispatcher.add_handler(unknown_handler)

# Запрашиваем обновления с сервера (вдруг новые сообщения кто прислал)
updater.start_polling()
