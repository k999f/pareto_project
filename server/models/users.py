from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase


class UsersModel:
    def __init__(self, role):
        self.permission = role

    # добавление пользователя (если успешно, то возвращает id нового пользователя, иначе - None)
    def insert_users(self, login, password, role):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO users
                              (login, password, role)
                              values (%s, %s, %s)
                              ON CONFLICT DO NOTHING
                              RETURNING id""", (login, password, role,))
            result = str(cursor.fetchone())
        return result

    def update_users(self, id, password, role):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""UPDATE users
                              SET password = %s, role = %s
                              WHERE id = %s""", (password, role, id,))

    def get_users(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, login, role
                              FROM users
                              ORDER BY login DESC""")
            schema = ['id', 'login', 'role']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_roles(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT role
                              FROM role
                              WHERE role != 'auth'""")
            schema = ['name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_user_data(self, user_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, login, password, role
                              FROM users
                              WHERE id = %s""", (user_id,))
            schema = ['id', 'login', 'password', 'role']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result