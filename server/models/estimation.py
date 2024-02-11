from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase


class EstimationModel:
    def __init__(self, role):
        self.permission = role

    # Получение информации о расчетах в проекте
    def get_estimations(self, project_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, name, created
                              FROM estimation
                              WHERE project_id = %s
                              ORDER BY created DESC""", (project_id,))
            schema = ['id', 'name', 'created']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_estimation_data(self, estimation_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT estimation.id, estimation.name, estimation.created, estimation.first_front, estimation.second_front, estimation.reference_set, estimation.output_data, i.name
                              FROM estimation JOIN indicator i ON i.id = indicator_id
                              WHERE estimation.id = %s""", (estimation_id,))
            schema = ['id' ,'name', 'created', 'first_front',
                      'second_front', 'reference_set', 'output_data', 'indicator_name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def insert_estimation(self, project_id, name, indicator, first_front, second_front, reference_set):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO estimation 
                              (project_id, name, indicator_id, first_front, second_front, reference_set)
                              values (%s, %s, %s, %s, %s, %s) RETURNING id""", (project_id, name, indicator, first_front, second_front, reference_set,))
            res = str(cursor.fetchone())
        result = res[1:len(res) - 2]
        return result

    def delete_estimation(self, estimation_id):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""DELETE FROM estimation
                              WHERE id = %s""", (estimation_id,))

    def update_results(self, estimation_id, indicator_results):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""UPDATE estimation
                              SET output_data = %s
                              WHERE id = %s""", (indicator_results, estimation_id,))

