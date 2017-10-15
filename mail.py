import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class MailNotifier():
    """Collect data about the experiment and its runs and send them via email after termination.

    Collect the start of the experiment and the result of each individual run. Summarize completed
    and failed runs at the end.
    """
    @classmethod
    def parse_mail(cls, config, results_path, name):
        """Parse config file and create an MailNotifier instance."""
        if "mail" in config:
            server= config["mail"]["server"]
            Mail = cls(server=server, results_path=results_path, name=name)
            if "user" in config["mail"]:
                Mail.user = config["mail"]["user"]
            if "password" in config["mail"]:
                Mail.password = config["mail"]["password"]
            return Mail
        else:
            return cls("", "", "", "")

    def __init__(self, server="", user = "", password = "", results_path="", name=""):
        self.server = server
        self.user = user
        self.password = password
        self.results_path = results_path
        self.name = name

        self.completed = 0
        self.failed = 0
        self.message = ""

    def start_experiment(self, command):
        """Record the start of the experiment in the mail body."""
        start_text = "Experiment {0} with variables {1} started\n"
        self.message += start_text.format(command.cmd, command.env)

    def save_complete(self, par_alloc, result):
        """Record the completion of one run in the mail body."""
        self.completed += 1
        complete_text = "    Completed run for configuration {0}\n"
        self.message += complete_text.format(par_alloc)

    def save_fail(self, par_alloc, error):
        """Record the failure of one run in the mail body."""
        self.failed += 1
        fail_text = "    Error {0} for run with configuration {1}\n"
        self.message += fail_text.format(error, par_alloc)

    def finish_experiment(self):
        """Record the termination of the experiment. Summarize completed and failed runs."""
        finish_text = "Experiment finished, {0} completed and {1} failed runs"
        self.message += finish_text.format(self.completed, self.failed)
        if self.server:
            self.send_mail()
            
    def send_mail(self):
        """Connect to the configured mailserver and send mail with attached result file."""
        smtp = None
        if self.user:
            smtp = smtplib.SMTP_SSL(self.server)
            smtp.ehlo()
            smtp.login(self.user, self.password)
        else:
            smtp = smtplib.SMTP(self.server)
            smtp.ehlo()
            self.user="Test@example.org"

        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = COMMASPACE.join(self.user)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = self.name + " - Results"

        msg.attach(MIMEText(self.message))
        
        with open(self.results_path, "rb") as result_file:
            result_attachment = MIMEApplication(result_file.read(),Name=self.name+'results.csv')
            result_attachment['Content-Disposition'] = 'attachment; filename="%s"' % (self.name+'results.csv')
            msg.attach(result_attachment)

        smtp.sendmail(self.user, self.user, msg.as_string())
        smtp.close()