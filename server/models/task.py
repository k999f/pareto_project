from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase
from psycopg2.extensions import AsIs


class TaskModel:
    def __init__(self, role):
        self.permission = role

    # Получение списка задач
    def get_tasks(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, name
                              FROM task WHERE type = 'standard'
                              ORDER BY id ASC""")
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def insert_task(self, name, data, type):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO task 
                              (name, data, type)
                              values (%s, %s, %s) RETURNING id""", (name, data, type,))
            res = str(cursor.fetchone())
        result = res[1:len(res) - 2]
        return result

    def delete_task(self, task_id):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""DELETE FROM task
                              WHERE id = %s""", (task_id,))

    def check_user_task(self, type, id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            if (type == "calculation"):
                cursor.execute("""SELECT t.id
                                FROM calculation JOIN task t ON t.id = task_id
                                WHERE t.type = 'user' AND calculation.id = %s""", (id,))
            elif (type == "analysis"):
                cursor.execute("""SELECT t.id
                                FROM tasks_in_analysis JOIN task t ON t.id = task_id
                                WHERE t.type = 'user' AND tasks_in_analysis.analysis_id = %s""", (id,))
            schema = ['id']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_calculation_used_tasks(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT task.id, task.name
                              FROM task JOIN calculation c ON c.task_id = task.id
                              WHERE type = 'standard'""")
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_analysis_used_tasks(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT task.id, task.name
                              FROM task JOIN tasks_in_analysis t ON t.task_id = task.id
                              WHERE type = 'standard'""")
            schema = ['id', 'name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def insert_task_parameter(self, task_id, task_parameter):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO task_parameters 
                              (task_id, parameter)
                              values (%s, %s)""", (task_id, task_parameter,))

    def get_tasks_parameters(self):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT task_parameters.task_id, task_parameters.parameter, t.name
                              FROM task_parameters JOIN task t ON t.id = task_parameters.task_id""")
            schema = ['id', 'parameter', 'task_name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_task_parameters_list(self, task_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT parameter
                              FROM task_parameters
                              WHERE task_id = %s""", (task_id,))
            schema = ['name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result