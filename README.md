# This is an open-source Discord ModMail Bot written in Python.

## Steps to self-host:
Clone the repository:
```bash
cd ~ && git clone https://github.com/lynix27/modmail-bot
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

You also need to set up a MySQL database server in order for the bot to work on multiple servers. If you already have a MySQL database server, put the credentials (`HOST`, `USER`, `PASSWORD` and `DB`) in a `.env` file. You also have to add a `TOKEN` variable that contains your bot's token. You can create a bot [here](https://discord.com/developers/applications). Head over to the "Bot" section and reset you token to get one. This is an example of how the file can look like:
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
