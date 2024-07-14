import aiomysql
import os
import strings.en
import strings.de
import strings.es
import strings.fr
import json

async def language_check(guild_id):
    with open("db.json", "r") as f:
        db = json.load(f)
    conn = await aiomysql.connect(
        host=db["HOST"],
        user=db["USER"],
        password=db["PASSWORD"],
        db=db["DB"],
        autocommit=True
    )
    cursor = await conn.cursor()
    await cursor.execute("SELECT LANGUAGE FROM languages WHERE SERVERID = %s", (int(guild_id),))
    result = await cursor.fetchone()
    await cursor.close()
    conn.close()
    if result is None:
        return strings.en
    
    if result[0] == "en":
        return strings.en
    
    if result[0] == "de":
        return strings.de
    
    if result[0] == "es":
        return strings.es
    
    if result[0] == "fr":
        return strings.fr