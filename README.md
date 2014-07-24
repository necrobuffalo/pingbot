pingbot
=====
Alliance pings made simple.

What is Pingbot?
----
Pingbot is an XMPP bot for pinging users on an Openfire-based jabber server using the Broadcast plugin. The bot is targeted specifically for use on Bohica Empire alliance services, and will thus require the use of 0mni's eve_api Drupal module at some point in the future.

Installation
----
Ensure you have Python 3.4, virtualenv, and git installed.
Create and activate a virtualenv.
```bash
virtualenv venv
venv/bin/activate
```
Download the development version and install dependencies.
```bash
git clone https://github.com/necrobuffalo/pingbot.git
cd pingbot
pip install -r requirements.txt
```
Edit settings.py as appropriate for your setup.

Usage
----
```bash
python runbot.py
```

Contributors
----
* Emma Barber/Taron Skeldara (https://github.com/necrobuffalo)
* Mr Majestic