import aiosqlite


def update_format_with_args(sql, parameters: dict):
    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)
    return sql, tuple(parameters.values())


def get_format_args(sql, parameters: dict):
    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])
    return sql, tuple(parameters.values())


class Database:
    path_to_db = 'data/database.sqlite'

    async def check_database(self):
        async with aiosqlite.connect(self.path_to_db) as db:
            await db.execute('CREATE TABLE IF NOT EXISTS users(user_id INTEGER, username TEXT, is_user INTEGER,'
                             ' address TEXT, phone TEXT, pc_ip TEXT)')
            await db.commit()

    async def add_user(self, user_id, username):
        async with aiosqlite.connect(self.path_to_db) as db:
            await db.execute("INSERT INTO users "
                             "(user_id, username, is_user)"
                             "VALUES (?, ?, ?)",
                             [user_id, username, 0])
            await db.commit()

    async def update_user(self, user_id, **kwargs):
        async with aiosqlite.connect(self.path_to_db) as db:
            sql = f"UPDATE users SET XXX WHERE user_id = {user_id}"
            sql, parameters = update_format_with_args(sql, kwargs)
            await db.execute(sql, parameters)
            await db.commit()

    async def get_user(self, **kwargs):
        async with aiosqlite.connect(self.path_to_db) as db:
            sql = "SELECT * FROM users WHERE "
            sql, parameters = get_format_args(sql, kwargs)
            get_response = await db.execute(sql, parameters)
            get_response = await get_response.fetchone()
        return get_response

    async def get_all_users(self):
        async with aiosqlite.connect(self.path_to_db) as db:
            sql = "SELECT * FROM users "
            get_response = await db.execute(sql)
            get_response = await get_response.fetchall()
        return get_response