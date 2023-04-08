# electrobot

Twitch chat bot that among other things manages predictions via chat commands. And start predictions based on Livesplit splits.

# Prerequisites

- [Python](https://www.python.org/downloads/) (Add to PATH during installation)
- [Livesplit](https://livesplit.org/downloads/) and [Livesplit Server](https://github.com/LiveSplit/LiveSplit.Server)
- A Twitch account (Affiliate) (with 2FA enabled)
- A Twitch bot account (you CAN use your streaming account)

# Installation

1. Download the ZIP file and extract.
2. Open a command prompt by typing `cmd` in the address bar of that folder
3. Type the following command to install the necessary packages:

```python
pip install -r requirements.txt
```

# Configuration

## Register Application

Since electrobot runs locally you must [register your own app](https://dev.twitch.tv/docs/authentication/register-app/) with Twitch, this only takes a few minutes.
Follow their instructions and you should end up with an application in [your console](https://dev.twitch.tv/console/apps).

Once you see your application click on manage.

1. Give the application a unique name
2. Set **OAuth Redirect URLs** to http://localhost:8777
 The port doesn't really matter as long as it's not used elsewhere.
3. In **Category** choose Chat Bot.
4. Click I'm not a robot, then Save
5. Take note of the **Client ID**, we will need this shortly.
6. Click on New Secret and also note this down.
7. Save

## Config.toml

Open the `config` folder.

1. Copy `config-example.toml` and rename the copy to `config.toml`.
2. Open `config.toml` and change the value in `CLIENT_ID` to the client ID you noted down earlier.
3. Do the same thing with `CLIENT_SECRET` and `REDIRECT_URI`. If you used localhost:8777 this one is already filled in.
4. If you didn't use port 8777 you **MUST** also change the `PORT` field under `[socket]` as by default it is set to 8777.
5. Under `[irc]` change the value of `CHANNEL` to your Twitch channel. **NOTE**: this must be in lowercase.
6. Finally change the value of `BOT_ACCOUNT` to the Twitch channel of your bot.
7. Save

## Prediction.json

In the `predictions` folder you find `predictions.json`. This is where you manage a list of predictions that the bot can start either by Livesplit or chat command. Try to open this file.

1. In the `name` field you choose the name of the prediction. This is how you call the prediction from chat. **NOTE**: This must be a string without spaces. So instead of calling it `my name` call it `my_name`
2. In `auto_predict` set `auto_start` to `true` if you want the prediction to start automatically based on Livesplit. If not, set to `false`
3. If you set `auto_start` to `true`, you must fill in `split_name` with a split name in Livesplit. When this split starts, a prediction will start, unless a prediction is still active.
4. In `data` set `title` to your prediction title. This is what your viewers will see when a prediction starts. For example: *Will I beat this level today?* Maximum of 45 characters.
5. In `outcomes` you can add a maximum of 10 different outcomes with a minimum of 2. Each of them requires a `title`. Maximum of 25 characters
6. In `prediction_window` you set the time in seconds that the prediction will run for with a minimum of 30 and maximum of 1800 (30 minutes).
7. You can create as many predictions as you want. 
8. Make sure the JSON data is valid by using an online tool like https://jsonformatter.org/ or https://jsonlint.com/

# Usage

Run `authorize.py`. The script will ask you whether to authenticate with a bot or streamer account and will then open your default browser. Make sure to authorize the right account after typing in `bot` or `streamer`.

You need to run `authorize.py` twice (once for streamer account and once for bot account). You can use your streaming account as bot if you want to. Make sure the bot is a moderator in your channel.

Run `electrobot.py` to start the bot

- Start predictions with `pred start <name>`
    - `name` must correspond to the `name` field of a prediction in `predictions.json`
- Lock predictions with `pred lock`
- Resolve predictions with `pred outcome <1-10>`
- Cancel predictions with `pred cancel`

You can make predictions start automatically based on Livesplit splits by using the [Livesplit Server](https://github.com/LiveSplit/LiveSplit.Server) component. You know it works when you right click on Livesplit, click Control and Start Server should be there. Make sure to launch Livesplit Server **before** you start the bot.

If you've configured `predictions.json` correctly a prediction should start when the given split name starts.


