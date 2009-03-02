#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
#          Frederico Silva Ribeiro <ribeiro.fsilva@gmail.com>
#          Guilherme Polo <ggpolo@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os.path
from smtplib import SMTP
from socket import sslerror

# Import the "right" parts from email.
# Importing email.MIMEMultipart while under Python 2.5 and newer causes
# trouble when running py2exe because it is a lazy import, so we import
# the correct, and direct, names.
try:
    # Make py2exe collect the next two modules so the other following
    # imports succeed, and, the module also work when sending emails.
    # (Noticeable just while running the py2exed version, but this is
    # really a Python issue since it is the one that is using old names
    # inside the email package causing lazy imports).
    from email import iterators
    from email import generator

    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.utils import formatdate
    from email import encoders as Encoders
except ImportError:
    # Python 2.4 and older
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.Utils import formatdate
    from email import Encoders

from umit.core.UmitLogging import log


class Email(object):
    """This class provides a simple interface for sending emails."""

    def __init__(self, from_addr, to_addr, server, localdomain=None,
            login=None, login_passwd=None, tls=False, port=25):
        """
        from_addr       The address from which the email should be sent.
        to_addr         The email address to where the scan result should be
                        sent.
        server          The address of the SMTP server which will deliver the
                        email.
        localdomain     If you want to send your email using your own domain,
                        set it here.
        login           If the mail server doesn't do relay, you should
                        authenticate with a login.
        login_passwd    If the mail server doesn't do relay, you should
                        authenticate on it.
        tls             True if the server requires tls, false otherwise.
        port            The port which the SMTP server is listening.
        """

        self.from_addr = from_addr
        self.to_addr = to_addr
        self.server = server
        self.localdomain = localdomain
        self.login = login
        self.login_passwd = login_passwd
        self.tls = tls
        self.port = port


    def connect(self):
        log.debug(">>> Connecting to smtp server at %s:%s as %s" % (
            self.server, self.port, self.localdomain))

        self.email_server = SMTP(self.server, self.port, self.localdomain)
        log.debug(">>> Connected!")

        log.debug(">>> EHLO %s" % self.from_addr)
        self.email_server.ehlo(self.from_addr)

        if self.tls:
            log.debug(">>> STARTTLS")
            self.email_server.starttls()

            log.debug(">>> EHLO %s" % self.from_addr)
            self.email_server.ehlo(self.from_addr)

        if self.login_passwd:
            log.debug(">>> LOGIN %s@%s" % (self.login, self.login_passwd))
            self.email_server.login(self.login, self.login_passwd)


    def sendmail(self, subject, msg, attach=False):
        """
        subject     The subject of the mail.
        msg         The message to send.
        attach      A list of attachments to send, or a single item.
        """
        try:
            self.email_server
        except AttributeError:
            self.connect()

        try:
            mail = self.create_mail(subject, msg, attach)
            log.debug(">>> SENDMAIL \n%s" % mail.as_string())

            self.email_server.sendmail(
                    self.from_addr,
                    self.to_addr,
                    mail.as_string())

            log.debug(">>> SENT!")
            return True
        except sslerror:
            return True

    def close(self):
        log.debug(">>> CLOSE")
        self.email_server.close()
        del(self.email_server)


    def __del__(self):
        """Always close the connection when the instance turns into garbage
        and is deleted or his reference counts turns to zero.
        """
        self.close()


    def create_mail(self, subject, msg, attach=False):
        mail = MIMEMultipart()
        mail['From'] = self.from_addr

        if isinstance(self.to_addr, list):
            mail['To'] = ', '.join(self.to_addr)
        else:
            mail['To'] = self.to_addr

        mail['Date'] = formatdate(localtime=True)
        mail['Subject'] = subject
        mail.attach(MIMEText(msg))

        if attach:
            if isinstance(attach, basestring):
                attach = (attach,)

            for atc in attach:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(atc, "rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(atc))
                mail.attach(part)

        return mail


if __name__ == "__main__":
    email = Email(
            "from_addr@gmail.com",
            "to_addr@gmail.com",
            "smtp.gmail.com",
            None,
            "login@gmail.com",
            "passwd",
            True,
            587)

    email.sendmail("Teste1", "Mensagem de teste 1", [
        "/Users/adriano/umit/trunk/umit",
        "/Users/adriano/umit/trunk/setup.py"])

    email.sendmail("Teste2", "Mensagem de teste 2",
            "/Users/adriano/umit/trunk/setup.nsi")

    email.sendmail("Teste3", "Mensagem de teste 3")
