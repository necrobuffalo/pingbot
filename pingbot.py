#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import time
import re
import sys

import sleekxmpp

import settings

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class PingBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will greets those
    who enter the room, and acknowledge any messages
    that mentions the bot's nickname.
    """

    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # Set the SSL version so that the bot will cooperate with openfire.
        import ssl
        self.ssl_version = ssl.PROTOCOL_SSLv3

        self.room = room
        self.nick = nick

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The groupchat_message event is triggered whenever a message
        # stanza is received from any chat room. If you also also
        # register a handler for the 'message' event, MUC messages
        # will be processed by both handlers.
        self.add_event_handler("groupchat_message", self.muc_message)


    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)

    def muc_message(self, msg):
        """
        Process incoming message stanzas from any chat room. Be aware
        that if you also have any handlers for the 'message' event,
        message stanzas may be processed by both handlers, so check
        the 'type' attribute when using a 'message' event handler.

        If a ping request is received, broadcast to the appropriate groups.

        IMPORTANT: Always check that a message is not from yourself,
                   otherwise you will create an infinite loop responding
                   to your own messages.

        This handler will reply to messages that mention
        the bot's nickname.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        command = re.split(" ", msg['body'], 1)
        timestamp = time.strftime("%a, %d %b %Y at %H:%M:%S UTC", time.gmtime())
        separator = u"\u0023" * 6 + " PING " + u"\u0023" * 6

        if command[0].lower() == '!ping' or command[0].lower() == '!p':
            params = re.split(" ", command[1], 1)
            if len(re.findall("\w+", params[0])) > 1:
                self.send_message(mto=msg['from'].bare,
                                  mbody="That is not a valid group name.",
                                  mtype='groupchat')
            else:
                self.send_message(mto="%s@%s" % (params[0], settings.OPENFIRE_BROADCAST_SERVICENAME),
                              mbody="\n%s\n\nMessage: %s\nSent from user %s to group %s on %s\n\n%s" % (separator,
									                                                                    params[1],
                                                                                                        msg['mucnick'],
                                                                                                        params[0],
                                                                                                        timestamp,
									                                                                    separator))

        elif command[0].lower() == '!help' or command[0].lower() == '!h':
            self.send_message(mto=msg['from'].bare,
                              mbody="Type !ping group_name yourmessage to ping.",
                              mtype='groupchat')

        elif command[0].lower() == '!majestic':
            self.send_message(mto=msg['from'].bare,
                              mbody="Holy shit, this is amazing",
                              mtype='groupchat')

        elif command[0].lower() == '!msg' or command[0].lower() == '!m':
            params = re.split(" ", command[1], 1)
            self.send_message(mto="%s@bohicaempire.com" % (params[0]),
                              mbody="Message: %s\nFrom: %s" % (params[1], msg['mucnick']))

    def muc_online(self, presence):
        """
        Process a presence stanza from a chat room. In this case,
        presences from users that have just come online are
        handled by sending a welcome message that includes
        the user's nickname and role in the room.

        Arguments:
            presence -- The received presence stanza. See the
                        documentation for the Presence stanza
                        to see how else it may be used.
        """
        if presence['muc']['nick'] != self.nick:
            self.send_message(mto=presence['from'].bare,
                              mbody="Hello, %s %s" % (presence['muc']['role'],
                                                      presence['muc']['nick']),
                              mtype='groupchat')
