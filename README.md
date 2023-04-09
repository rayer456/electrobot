# electrobot

Twitch chat bot that among other things manages predictions via chat commands and starts predictions based on Livesplit.

# Prerequisites

- [Python](https://www.python.org/downloads/)
- [Livesplit](https://livesplit.org/downloads/) and [Livesplit Server](https://github.com/LiveSplit/LiveSplit.Server) (Optional)
- A Twitch account (Affiliate) (with 2FA enabled)
- A Twitch bot account

# Installation

1. Download the ZIP file and extract.
2. Run the following command:
    ```
    pip install -r requirements.txt
    ```

# Configuration

## Register Application

Since the bot runs locally you must [register your own app](https://dev.twitch.tv/docs/authentication/register-app/) with Twitch, this only takes a few minutes.
Follow their instructions and you should end up with an application in [your console](https://dev.twitch.tv/console/apps).

Once you see your application click on manage, then

1. Give the application a unique name
2. Set **OAuth Redirect URLs** to http://localhost:8777.
 The port doesn't really matter as long as it's not used elsewhere.
3. In **Category** choose Chat Bot.
4. Click I'm not a robot, then Save
5. Take note of the **Client ID**, you will need this shortly.
6. Click on **New Secret** and also note this down.
7. Save

## Config.toml

Open the `config` folder.

1. Copy `config-example.toml` and rename the copy to `config.toml`.
2. Open `config.toml` and change the value in `CLIENT_ID` to the client ID you noted down earlier.
3. Do the same thing with `CLIENT_SECRET` and `REDIRECT_URI`.
4. If you didn't use port 8777 you **MUST** also change the `PORT` field under `[socket]` as by default it is set to 8777.
5. Under `[irc]` change the value of `CHANNEL` to your Twitch channel. **NOTE**: this must be in lowercase.
6. Finally change the value of `BOT_ACCOUNT` to the Twitch channel of your bot.
7. Save

## Predictions.json

Open the `predictions` folder, make a copy of `predictions-example.json` and rename this copy to `predictions.json`, then open the file.

This is where you manage a list of "pre-made" predictions that the bot can start either by Livesplit or chat command. You can create as many predictions as you want.

- In the `name` field you choose the name of the prediction. This is how you call the prediction from chat. **NOTE**: This must be a string without spaces. So instead of calling it `level one` call it `level_one`.
    ```json
    "name": "bike"
    ```
- Set `auto_start` to `true` if you want the prediction to start automatically based on Livesplit. If not, set to `false`. If you set `auto_start` to `true`, you must fill in `split_name` with a split name in Livesplit. When this split starts, a prediction will start, unless a prediction is still active. 
    ```json
    "auto_predict": {
                    "auto_start": true,
                    "split_name": "complications"
                    }
    ```
- In `data` set `title` to your prediction title. This is what your viewers will see when a prediction starts. Maximum of 45 characters.
    ```json
    "title": "Parked bike?"
    ```
- In `outcomes` you can add a maximum of 10 different outcomes with a minimum of 2. Each of them requires a `title`. Maximum of 25 characters.
    ```json
    {
        "title": "yes"
    },
    {
        "title": "no"
    }
    ```
- In `prediction_window` you set the time in seconds that the prediction will run for with a minimum of 30 and maximum of 1800 (30 minutes).
    ```json
    "prediction_window": 600
    ``` 
- Make sure the JSON data is valid by using an online tool like https://jsonformatter.org/ or https://jsonlint.com/

# Usage

## Authorization

Run `authorize.py`. The script will ask you to authorize with a bot or streamer account and will then open your default browser. Make sure to authorize the correct account.

You need to run `authorize.py` **twice**, once for a streamer account and once for a bot account. You can use your streaming account as bot if you want to. Make sure the bot is a moderator in your channel.

If both accounts are authorized you should only need to rerun `authorize.py` if you change your Twitch password or disconnect the integration which you can do on [this page](https://www.twitch.tv/settings/connections) under **Other connections**.

## Livesplit

You can make predictions start automatically based on Livesplit splits by using the [Livesplit Server](https://github.com/LiveSplit/LiveSplit.Server) component. You know it works when you right click on Livesplit, Control and Start Server should be there. 

Make sure to start Livesplit Server **before** you start the bot.

If you've configured `predictions.json` correctly a prediction should start when the given split name starts. 

The default port on which Livesplit Server runs is 16834, if you use a different port, you must also change the port in `config.toml` under `[livesplit]`.

## Starting the bot

Run `electrobot.py`

**Chat commands:**

The broadcaster and moderators can use these commands.
- Start predictions with `pred start <name>`
    - `name` must correspond to the `name` field of a prediction in `predictions.json`
    - ![](/assets/pred_start.png)
- Lock predictions with `pred lock` or wait until the timer runs out
    - ![](/assets/pred_lock.png)
- Resolve predictions with `pred outcome <1-10>`
    - ![](/assets/pred_outcome.png)
- Cancel predictions with `pred cancel`
    - ![](/assets/pred_cancel.png)

**Self-starting predictions:**

![](/assets/livesplit.gif)