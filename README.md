# This is an open-source Discord ModMail Bot written in Python.

## Steps to self-host:
Clone the repository:
```bash
git clone https://github.com/vxsualized/modmail-bot
```
Navigate to the newly created directory:
```bash
cd modmail-bot
```
Install the dependencies by using:
```bash
pip install -r requirements.txt -y
```
or
```bash
pip install aiomysql cryptography discord.py jishaku python-dotenv -y
```

You also need to set up a MySQL database server in order for the bot to work on multiple servers. If you already have a MySQL database server, put the credentials (`HOST`, `USER`, `PASSWORD` and `DB`) in a `.env` file. You also have to add a `TOKEN` variable that contains your bot's token. You can create a bot [here](https://discord.com/developers/applications). Head over to the "Bot" section and reset your token to get one. This is an example of how the file can look like:
```
TOKEN = ...

HOST = localhost
USER = lynix
PASSWORD = password
DB = modmail
```

Run the script by using:
```bash
python3 main.py
```
(This command may vary based on your OS.)

## If you don't want to self-host the bot, you can invite the official instance by clicking [here](https://discord.com/api/oauth2/authorize?client_id=1139964189465653358&permissions=8&scope=bot)!

## Adding translations
Go to [this file](./strings/en.py) and copy it's content. Fork this repository. Create a new Python file in the [strings folder](./strings), name it like your language's language tag and translate **ONLY THE STRINGS, NOT THE STRING NAMES**. Create a pull request.
