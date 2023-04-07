# electrobot

Twitch chat bot that among other things manages predictions via chat commands.

## Prerequisites

- [Python](https://www.python.org/downloads/) (Add to PATH during installation)
- A Twitch account (with 2FA enabled)
- A Twitch bot account (you CAN use your streaming account)

## Installation

1. Download the ZIP file and extract in a folder
2. Open a command prompt by typing `cmd` in the address bar of that folder
3. Type the following command to install the necessary packages:

```python
pip install -r requirements.txt
```

## Configuration

Since electrobot runs locally you must [register your own app](https://dev.twitch.tv/docs/authentication/register-app/) with Twitch, this only takes a few minutes.
Follow their instructions and you should end up with an application in [your console](https://dev.twitch.tv/console/apps).

Once you see your application click on manage.

- Give the application a unique name
- Set **OAuth Redirect URLs** to `http://localhost:8777`.
 The port doesn't really matter as long as it's not used elsewhere.
- In **Category** choose Chat Bot.
- Click I'm not a robot, then Save
- Take note of the **Client ID**, we will need this shortly.
- Click on New Secret and also note this down.
- Save

Head back to the folder where you extracted electrobot and open the `config` folder.

1. Copy `config-example.toml` and rename the copy to `config.toml`.
2. Open `config.toml` and change the value in `CLIENT_ID` to the client ID you noted down earlier.
3. Do the same thing with `CLIENT_SECRET` and `REDIRECT_URI`. If you used localhost:8777 this is already filled in.
4. If you didn't use port 8777 you **MUST** also change the `PORT` field under `[socket]` as by default it is set to 8777.
5. Under `[irc]` change the value in `CHANNEL` to your Twitch channel. **NOTE**: this must be in lowercase.
6. Finally change the value in `BOT_ACCOUNT` to the Twitch channel of your bot.
7. Save

## Usage
authorize.py
electrobot.py















