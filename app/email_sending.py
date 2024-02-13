
import abc
from smtplib import SMTP_SSL
from email.utils import make_msgid
from email.message import EmailMessage

import config


class EmailBase(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def email_from(self):
        pass

    def __init__(self, email_to):
        self.email_to = email_to

    @abc.abstractmethod
    def get_html(self, cid):
        pass

    @abc.abstractmethod
    def get_content(self):
        pass

    @abc.abstractmethod
    def get_subject(self):
        pass


class EmailRegistration(EmailBase):
    email_from = config.APP_EMAIL

    def __init__(self, email_to, link_to_finish_registration):
        super().__init__(email_to)
        assert link_to_finish_registration, "Param 'link_to_finish_registration' must be non zero length string."
        self.link_to_finish = link_to_finish_registration

    def get_subject(self):
        return "Finish registration on {app}".format(app=config.APP_NAME)

    def get_html(self, cid):
        return """\
        <html>
          <head></head>
          <body>
            <p>Hello from {app_name}!</p>
            <p>Follow
                <a href="{link_to_finish}">link</a> to finish the registration.
            </p>
            <img src="cid:{asparagus_cid}" />
          </body>
        </html>
        """.format(app_name=config.APP_NAME, link_to_finish=self.link_to_finish,
                   asparagus_cid=cid)

    def get_content(self):
        return "Hello from {app_name}! Follow link {link_to_finish} to finish the registration.".format(
            app_name=config.APP_NAME, link_to_finish=self.link_to_finish
        )


def send_email(email_obj: EmailBase, use_html=True):
    msg = EmailMessage()

    msg['Subject'] = email_obj.get_subject()
    msg['From'] = email_obj.email_from
    msg['To'] = email_obj.email_to
    msg.set_content(email_obj.get_content())

    if use_html:
        asparagus_cid = make_msgid()[1:-1]
        msg.add_alternative(email_obj.get_html(asparagus_cid), subtype='html')

    server = SMTP_SSL(config.APP_EMAIL_HOST, config.APP_EMAIL_PORT)
    server.login(config.APP_EMAIL, config.APP_EMAIL_PASSWORD)

    server.send_message(msg)
    server.quit()
