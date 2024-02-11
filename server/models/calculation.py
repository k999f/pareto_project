from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase


class CalculationModel:
    def __init__(self, role):
        self.permission = role

    # Получение информации о расчетах в проекте
    def get_calculations(self, project_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, name, created
                              FROM calculation
                              WHERE project_id = %s
                              ORDER BY created DESC""", (project_id,))
            schema = ['id', 'name', 'created']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_calculation_data(self, calculation_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT calculation.id, calculation.name, calculation.created, calculation.approximation, calculation.indicators, calculation.algorythm_parameters, calculation.task_parameters, a.name, t.name, t.data
                              FROM calculation JOIN algorythm a ON a.id = algorythm_id
                              JOIN task t ON t.id = task_id
                              WHERE calculation.id = %s""", (calculation_id,))
            schema = ['id' ,'name', 'created', 'approximation', 'indicators', 'algorythm_parameters', 'task_parameters', 'algorythm', 'task_name', 'task_data']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result


    def insert_calculation(self, project_id, name, task, algorythm, algorythm_parameters, task_parameters):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO calculation 
                              (project_id, name, task_id, algorythm_id, algorythm_parameters, task_parameters)
                              values (%s, %s, %s, %s, %s, %s) RETURNING id""", (project_id, name, task, algorythm, algorythm_parameters, task_parameters,))
            res = str(cursor.fetchone())
        result = res[1:len(res) - 2]
        return result

    def delete_calculation(self, calculation_id):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""DELETE FROM calculation
                              WHERE id = %s""", (calculation_id,))

    def update_results(self, calculation_id, approximation, indicators):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""UPDATE calculation
                              SET approximation = %s, indicators = %s
                              WHERE id = %s""", (approximation, indicators, calculation_id,))


    def get_results(self, calculation_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT indicators, approximation
                              FROM calculation
                              WHERE id = %s""", (calculation_id,))
            schema = ['indicators', 'approximation']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result