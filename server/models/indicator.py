from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase


class IndicatorModel:
    def __init__(self, role):
        self.permission = role

    # Получение списка индикаторов
    def get_indicators(self, type):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, name
                              FROM indicator
                              WHERE type = %s
                              ORDER BY id ASC""", (type,))
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_used_indicators(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT indicator.id, indicator.name
                              FROM indicator JOIN estimation e ON e.indicator_id = indicator.id""")
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def delete_indicator(self, indicator_id):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""DELETE FROM indicator
                              WHERE id = %s""", (indicator_id,))

    def insert_indicator(self, name, type):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO indicator 
                              (name, type)
                              values (%s, %s) RETURNING id""", (name, type,))
            res = str(cursor.fetchone())
        result = res[1:len(res) - 2]
        return result