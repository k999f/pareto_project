from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase


class AlgorythmModel:
    def __init__(self, role):
        self.permission = role

    # Получение списка алгоритмов
    def get_algorythms(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, name
                              FROM algorythm
                              ORDER BY id ASC""")
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def insert_algorythm(self, name):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO algorythm 
                              (name)
                              values (%s) RETURNING id""", (name,))
            res = str(cursor.fetchone())
        result = res[1:len(res) - 2]
        return result

    def insert_algorythm_parameter(self, algorythm_id, algorythm_parameter):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO algorythm_parameters 
                              (algorythm_id, parameter)
                              values (%s, %s)""", (algorythm_id, algorythm_parameter,))

    def get_calculation_used_algorythms(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT algorythm.id, algorythm.name
                              FROM algorythm JOIN calculation c ON c.algorythm_id = algorythm.id""")
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_analysis_used_algorythms(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT algorythm.id, algorythm.name
                              FROM algorythm JOIN analysis a ON a.algorythm_id = algorythm.id""")
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def delete_algorythm(self, algorythm_id):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""DELETE FROM algorythm
                              WHERE id = %s""", (algorythm_id,))

    def get_algorythms_parameters(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT algorythm_parameters.algorythm_id, algorythm_parameters.parameter, a.name
                              FROM algorythm_parameters JOIN algorythm a ON a.id = algorythm_parameters.algorythm_id""")
            schema = ['id', 'parameter', 'algorythm_name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_algorythm_parameters_list(self, algorythm_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT parameter
                              FROM algorythm_parameters
                              WHERE algorythm_id = %s""", (algorythm_id,))
            schema = ['name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result
