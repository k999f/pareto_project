from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from DBCM import UseDatabase


class ProjectModel:
    def __init__(self, role):
        self.permission = role

    # получение информации о всех проектах
    def get_projects(self, user_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT id, name, created, modified, description
                              FROM project
                              WHERE user_id = %s
                              ORDER BY created DESC""", (user_id,))
            schema = ['id', 'name', 'created', 'modified', 'description']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def insert_project(self, user_id, name, description):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""INSERT INTO project 
                              (user_id, name, description)
                              values (%s, %s, %s) RETURNING id""", (user_id, name, description,))
            res = str(cursor.fetchone())
        result = res[1:len(res) - 2]
        return result

    def delete_project(self, project_id):
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""DELETE FROM project
                              WHERE id = %s""", (project_id,))

    def get_project_name(self, project_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""SELECT name
                              FROM project
                              WHERE id = %s""", (project_id,))
            schema = ['name']
            for con in cursor.fetchall():
                result.append(dict(zip(schema, con)))
        return result

    def update_modified_date(self, project_id):
        result = []
        with UseDatabase(current_app.config['db'][self.permission]) as cursor:
            cursor.execute("""UPDATE project
                              SET modified = current_date
                              WHERE id = %s""", (project_id,))
