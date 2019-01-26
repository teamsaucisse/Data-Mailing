import re

from mail_app.mail import Mail
from mail_app.mail_processors.abstract_processor import AbstractProcessor
from mail_app.processed_mail import ProcessedMail

class PromoCodeProcessor(AbstractProcessor):

    general_keywords = ["voucher", "promo code", "promocode", "offer", "code", "\d\d?% off", "reduction", "£\d\d?\d? off"]

    def __init__(self):
        super().__init__()
        self.category = "Promo code"

    def process(self, mail):
        if self.__general_conditions(mail):
            return ProcessedMail(self.category, mail.body, mail.time, mail.attachments)

    ############################################ Conditions ############################################

    def __general_conditions(self, mail: Mail):
        return (mail.attachments or
            any(re.search(mail.body.lower(), keyword) for keyword in self.ticket_keyword)) and \
           (any(re.search(mail.subject.lower(), keyword) for keyword in self.general_keywords) or
            any(re.search(mail.body.lower(), keyword) for keyword in self.general_keywords) or
            any(re.search(attachment["name"].lower(), keyword) for attachment in mail.attachments for keyword in
                self.general_keywords))