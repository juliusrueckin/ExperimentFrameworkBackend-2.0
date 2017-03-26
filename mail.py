import smtplib
from email.mime.text import MIMEText

class MailNotifier():
    """Collect data about the experiment and its runs and send them via email after termination.

    Collect the start of the experiment and the result of each individual run. Summarize completed
    and failed runs at the end.
    """
    @classmethod
    def parse_mail(cls, config):
        """Parse config file and create an MailNotifier instance."""
        if "mail" in config:
            server= config["mail"]["server"]
            Mail = cls(server=server)
            if "user" in config["mail"]:
                Mail.user = config["mail"]["user"]
            if "password" in config["mail"]:
                Mail.password = config["mail"]["password"]
            Mail.cmd = config["cmd"]
            Mail.env = config["env"]
            return Mail
        else:
            return cls("", "")

    def __init__(self, server="", user = "", password = "", cmd = "", env = ""):
        self.server = server
        self.user = user
        self.password = password
        self.cmd = cmd
        self.env = env
        self.completed = 0
        self.failed = 0
        self.message = ""

    def start_experiment(self):
        """Record the start of the experiment in the mail body."""
        start_text = "Experiment {0} with variables {1} started\n"
        self.message += start_text.format(self.cmd, self.env)

    def save_complete(self, par_alloc):
        """Record the completion of one run in the mail body."""
        self.completed += 1
        complete_text = "    Completed run for configuration {0}"
        self.message += complete_text.format(par_alloc)

    def save_fail(self, par_alloc, error):
        """Record the failure of one run in the mail body."""
        self.failed += 1
        fail_text = "    Error {0} for run with configuration {1}"
        self.message += fail_text.format(error, par_alloc)

    def finish_experiment(self):
        """Record the termination of the experiment. Summarize completed and failed runs."""
        finish_text = "Experiment finished, {0} completed and {1} failed runs"
        self.message += finish_text.format(self.completed, self.failed)
        if self.server:
            self.send_mail()
            
    def send_mail(self):
        """Connect to the configured mailserver and send the mail."""
        s = None
        if self.user:
            s = smtplib.SMTP_SSL(self.server)
            s.ehlo()
            s.login(self.user, self.password)
        else:
            s = smtplib.SMTP(self.server)
            s.ehlo()
        content = MIMEText(self.message)
        content["Subject"] = "Experiment results"
        content["From"] = self.user
        content["To"] = self.user
        s.send_message(content)
        s.close()

    
