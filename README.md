# This is an open-source Discord ModMail Bot written in Python.

## Steps to self-host:
1. Install the dependencies by using:
```
pip install -r requirements.txt -y
```

2. You also need to set up a MySQL database server in order for the bot to work on multiple servers. If you already have a MySQL database server, put the credentials (`HOST`, `USER`, `PASSWORD` and `DB`) in a `.env` file. You also have to add a `TOKEN` variable that contains your bot's token. This is an example of how the file can look like:
```
TOKEN = ...

HOST = localhost
USER = lynix
PASSWORD = password
DB = modmail
```

3. Run the script by using:
```
python3 main.py
```
(This command varies depending on your operating system.)