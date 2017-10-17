from telegram.ext import Updater
import logging
from telegram import Bot

class TelegramNotifier():
    """Sends 
    """
    @classmethod
    def parse_telegram(cls, config):
        """Parse config file and create a TelegramNotifier instance."""
        if "telegram" in config:
            token = config["telegram"]["token"]
            chat_id = config["telegram"]["chat_id"]
            verbose = True if config["telegram"]["verbose"] else False
            bot = Bot(token)
            Telegram = cls(token, chat_id, bot, verbose)
            return Telegram
        else:
            return cls("", "", "", False)

    def __init__(self, token="", chat_id="", bot="", verbose=False):
        self.token = token
        self.chat_id = chat_id
        self.bot = bot
        self.verbose = verbose

        self.message = ""
        self.completed = 0
        self.failed = 0

    def start_experiment(self, command):
        """Record the start of the experiment and send telegram message."""
        start_text = "Experiment {0} with variables {1} started\n"
        self.message += start_text.format(command.cmd, command.env)
        self.send_message()

    def save_complete(self, par_alloc, result):
        """If verbose, record the completion of one run and send telegram message."""
        self.completed += 1
        if self.verbose:
            complete_text = "Completed run for configuration {0}\n"
            self.message = complete_text.format(par_alloc)
            self.send_message()

    def save_fail(self, par_alloc, error):
        """If verbose, record the failure of one run and send telegram message."""
        self.failed += 1

        if self.verbose:
            fail_text = "Error {0} for run with configuration {1}\n"
            self.message = fail_text.format(error, par_alloc)
            self.send_message()

    def finish_experiment(self):
        """Record the termination of the experiment. Summarize completed and failed runs."""
        finish_text = "Experiment finished, {0} completed and {1} failed runs"
        self.message += finish_text.format(self.completed, self.failed)
        self.send_message()
            
    def send_message(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.bot.send_message(chat_id=self.chat_id, text=self.message)