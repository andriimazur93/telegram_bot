#!/usr/bin/env python

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from config import Config
import os

PORT = int(os.environ.get('PORT', 8443))
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def callback_start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Hi! Memes bot was started')


def callback_alarm(context: CallbackContext):
    context.bot.send_message(chat_id=Config.TELEGRAM_CHANNEL_NAME, text='BEEP')


def callback_run(update: Update, context: CallbackContext):
    try:
        interval = int(context.args[0])
    except IndexError:
        interval = 5

    context.bot.send_message(chat_id=update.message.chat_id,
                             text=f'Setting a timer for {interval} seconds.')

    context.job_queue.run_repeating(callback_alarm, interval=interval, context=update.message.chat_id)


def callback_stop(update: Update, context: CallbackContext):
    update.message.reply_text('Stopping the timer...')
    remove_job_if_exists("callback_alarm", context)


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=Config.TELEGRAM_TOKEN, use_context=True)
    j = updater.job_queue

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", callback_start))
    dispatcher.add_handler(CommandHandler("run", callback_run))
    dispatcher.add_handler(CommandHandler("stop", callback_stop))

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=Config.TELEGRAM_TOKEN,
                          webhook_url=f"https://{Config.HEROKU_APP_NAME}.herokuapp.com/" + Config.TELEGRAM_TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
