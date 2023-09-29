import aiomysql
import os
import strings.en
import strings.de

async def language_check(guild_id):
    conn = await aiomysql.connect(
        host=os.getenv('HOST'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        db=os.getenv('DB'),
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