"""
    COPYRIGHT INFORMATION
    ---------------------

Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/
    
Otherwise, the modifications in this code, and all the code in the /lib directory, are copyright © WERUreo 2020.
"""

from irc.bot import SingleServerIRCBot
from requests import get

from lib import db, cmds, react
import config

NAME = "WERUreo"
OWNER = "werureo"

class Bot(SingleServerIRCBot):
    def __init__(self):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.USERNAME = NAME.lower()
        self.CLIENT_ID = config.CLIENT_ID
        self.TOKEN = config.OAUTH_TOKEN
        self.CHANNEL = f"#{OWNER.lower()}"

        url = f"https://api.twitch.tv/kraken/users?login={self.USERNAME}"
        headers = {"Client-ID": self.CLIENT_ID, "Accept": "application/vnd.twitchtv.v5+json"}
        resp = get(url, headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]

        super().__init__([(self.HOST, self.PORT, self.TOKEN)], self.USERNAME, self.USERNAME)

    def on_welcome(self, cxn, event):
        for req in ("membership", "tags", "commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")

        cxn.join(self.CHANNEL)
        db.build()
        self.send_message("lepBOT Now online. lepBOT")

    @db.with_commit
    def on_pubmsg(self, cxn, event):
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {"name": tags["display-name"], "id": tags["user-id"]}
        message = event.arguments[0]

        react.add_user(bot, user)

        if user["name"] != NAME:
            react.process(bot, user, message)
            cmds.process(bot, user, message)

        print(f"Message from {user['name']}: {message}")

    def send_message(self, message):
        self.connection.privmsg(self.CHANNEL, message)


if __name__ == "__main__":
    bot = Bot()
    bot.start()
