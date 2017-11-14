import sys
import email
import imaplib
import smtplib

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTextEdit, QMessageBox


class UI(QMainWindow):
    def __init__(self, *args):
        super().__init__(*args)
        loadUi('ui.ui', self)
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())
        self.button_start.clicked.connect(self.resend)

    @staticmethod
    def popup_message(text, level='information'):
        msg = QMessageBox()
        if level == 'information':
            msg.setIcon(QMessageBox.Information)
        elif level == 'warning':
            msg.setIcon(QMessageBox.Warning)
        elif level == 'critical':
            msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle(level.capitalize())
        msg.exec_()

    def resend(self):
        sender = self.findChild(QTextEdit, 'text_edit_sender').toPlainText()
        sender_password = self.findChild(QTextEdit, 'text_edit_password').toPlainText()
        recipient = self.findChild(QTextEdit, 'text_edit_recipient').toPlainText()

        if not (sender or sender_password or recipient):
            self.popup_message('All fields must be filled', 'warning')
            return

        mail_box = imaplib.IMAP4_SSL('imap.gmail.com')
        mail_box.login(sender, sender_password)
        mail_box.select('inbox', readonly=True)  # do not mark as seen

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(sender, sender_password)

        result, data = mail_box.uid('search', None, 'ALL')

        for mail_id in [mail_id for mail_id in data[0].decode().split()][::1]:
            _, data = mail_box.uid('fetch', mail_id, '(RFC822)')

            raw_email = data[0][1]
            mail = email.message_from_bytes(raw_email)
            del mail['Received']
            del mail['Message-ID']
            server.sendmail(sender, recipient, mail.as_string())

        server.quit()
        self.popup_message('Done')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = UI()
    widget.show()
    sys.exit(app.exec_())
