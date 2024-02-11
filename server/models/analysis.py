from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase


class AnalysisModel:
    def __init__(self, role):
        self.permission = role

    # Получение информации о расчетах в проекте
    def get_analyses(self, project_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, name, created
                              FROM analysis
                              WHERE project_id = %s
                              ORDER BY created DESC""", (project_id,))
            schema = ['id', 'name', 'created']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def insert_analysis(self, project_id, name, algorythm, algorythm_parameters):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO analysis 
                              (project_id, name, algorythm_id, algorythm_parameters)
                              values (%s, %s, %s, %s) RETURNING id""", (project_id, name, algorythm, algorythm_parameters,))
            res = str(cursor.fetchone())
        result = res[1:len(res) - 2]
        return result

    def insert_task_in_analysis(self, analysis_id, task):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            for t in task:
                cursor.execute("""INSERT INTO tasks_in_analysis 
                                (analysis_id, task_id)
                                values (%s, %s)""", (analysis_id, t,))

    def insert_analysis_task_parameters(self, analysis_id, task_id, task_parameters):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""UPDATE tasks_in_analysis 
                              SET task_parameters = %s
                              WHERE analysis_id = %s AND task_id = %s""", (task_parameters, analysis_id, task_id,))

    def get_analysis_data(self, analysis_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT analysis.id, analysis.name, analysis.created, analysis.output_data, a.name, analysis.algorythm_parameters
                              FROM analysis JOIN algorythm a ON a.id = algorythm_id
                              WHERE analysis.id = %s""", (analysis_id,))
            schema = ['id' ,'name', 'created', 'output_data', 'algorythm', 'algorythm_parameters']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def get_analysis_task(self, analysis_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT task.id, task.name, task.data, t.task_parameters
                              FROM task JOIN tasks_in_analysis t ON t.task_id = task.id
                              WHERE t.analysis_id = %s""", (analysis_id,))
            schema = ['id', 'name', 'data', 'parameters']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def delete_analysis(self, analysis_id):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""DELETE FROM analysis
                              WHERE id = %s""", (analysis_id,))

    def update_results(self, analysis_id, results):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""UPDATE analysis
                              SET output_data = %s
                              WHERE id = %s""", (results, analysis_id,))

