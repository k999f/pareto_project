from flask import render_template, request, redirect, Blueprint, url_for, session, current_app
from ..auth import auth
from models import project, calculation, analysis, estimation, algorythm, task, indicator
import socket
import time
import pickle
import threading

main_blueprint = Blueprint('main_blueprint', __name__,
                           template_folder='templates')


@main_blueprint.route('/', methods=['GET', 'POST'])
@auth.login_required
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
    chosen_project_id = request.args.get('project')
    #delete_project_id = request.args.get('delete_project')
    if request.method == 'GET':
        if chosen_project_id is not None:
            return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
        #elif delete_project_id is not None:
            #delete_project(delete_project_id)
            #return render_template('projects_list.html', projects=get_projects_list(session['user_id']), user=session['user'], role=session['role'])
        else:
            return render_template('projects_list.html', projects=get_projects_list(session['user_id']), user=session['user'], role=session['role'])
    elif request.method == 'POST':
        if 'create_project' in request.form:
            data = request.form
            create_new_project(data)
            return render_template('projects_list.html', projects=get_projects_list(session['user_id']), user=session['user'], role=session['role'])

        if 'delete_project' in request.form:
            delete_project_id = request.form['delete_project']
            project_calculations = get_project_calculations(delete_project_id)
            project_analyses = get_project_analyses(delete_project_id)
            for calculation in project_calculations:
                user_task = check_user_task("calculation", calculation['id'])
                if (user_task):
                    delete_task(user_task[0]['id'])
            for analysis in project_analyses:
                user_task = check_user_task("analysis", analysis['id'])
                if (user_task):
                    for t in user_task:
                        delete_task(t['id'])
            delete_project(delete_project_id)
            return render_template('projects_list.html', projects=get_projects_list(session['user_id']), user=session['user'], role=session['role'])
        
        if 'create_button' in request.form:
            value = request.form['create_button']
            if value == 'calculation':
                return render_template('create_calculation.html', algorythms=get_algorythms(), tasks=get_tasks(), algorythms_parameters=get_algorythms_parameters(), tasks_parameters=get_tasks_parameters(), user=session['user'], role=session['role'])
            if value == 'calculation_user_task':
                return render_template('create_calculation_user_task.html', algorythms=get_algorythms(), algorythms_parameters=get_algorythms_parameters(), user=session['user'], role=session['role'])
            if value == 'analysis':
                return render_template('create_analysis.html', algorythms=get_algorythms(), tasks=get_tasks(), algorythms_parameters=get_algorythms_parameters(), tasks_parameters=get_tasks_parameters(), user=session['user'], role=session['role'])
            if value == 'analysis_user_task':
                return render_template('create_analysis_user_task.html', algorythms=get_algorythms(), algorythms_parameters=get_algorythms_parameters(), tasks_parameters=get_tasks_parameters(), user=session['user'], role=session['role'])
            if value == 'estimation_unary':
                return render_template('create_estimation_unary.html', indicators=get_indicators("unary"), user=session['user'], role=session['role'])
            if value == 'estimation_binary':
                return render_template('create_estimation_binary.html', indicators=get_indicators("binary"), user=session['user'], role=session['role'])

        if 'save_button' in request.form:
            value = request.form['save_button']
            if value == 'calculation':
                data = request.form
                new_calculation_id = create_new_calculation(data, chosen_project_id, None)
                update_modified_date(chosen_project_id)
                app = current_app._get_current_object()
                computing_thread = threading.Thread(target=compute, args=(sock, "calculation", new_calculation_id, app, session['role'],))
                computing_thread.start()
                #compute(sock, "calculation", new_calculation_id)
                return render_template('look_calculation.html', calculation_data=get_calculation_data(new_calculation_id), user=session['user'], role=session['role'])
                #return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
            
            if value == 'calculation_user_task':
                data = request.form.to_dict()
                algorythm_parameters_separately = request.form.getlist('algorythm_parameter')
                task_name = request.files['task'].filename
                task_data = request.files['task'].read().decode("utf-8")
                task_id = insert_task(task_name, task_data, "user")
                data["task"] = task_id
                new_calculation_id = create_new_calculation(data, chosen_project_id, algorythm_parameters_separately)
                update_modified_date(chosen_project_id)
                app = current_app._get_current_object()
                computing_thread = threading.Thread(target=compute, args=(sock, "calculation", new_calculation_id, app, session['role'],))
                computing_thread.start()
                #compute(sock, "calculation", new_calculation_id)
                return render_template('look_calculation.html', calculation_data=get_calculation_data(new_calculation_id), user=session['user'], role=session['role'])
                #return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
            
            if value == 'analysis':
                data = request.form
                task = request.form.getlist('task')
                if task:
                    new_analysis_id = create_new_analysis(data, task, chosen_project_id, None)
                    update_modified_date(chosen_project_id)
                    app = current_app._get_current_object()
                    computing_thread = threading.Thread(target=compute, args=(sock, "analysis", new_analysis_id, app, session['role'],))
                    computing_thread.start()
                    #compute(sock, "analysis", new_analysis_id)
                    return render_template('look_analysis.html', analysis_data=get_analysis_data(new_analysis_id), analysis_task=get_analysis_task(new_analysis_id), user=session['user'], role=session['role'])
                    #return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), analysis_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
                else:
                    return render_template('create_analysis.html', algorythms=get_algorythms(), tasks=get_tasks(), analysis_data=data, user=session['user'], role=session['role'])
            
            if value == 'analysis_user_task':
                data = request.form
                task_files = request.files.getlist("task")
                task = list()
                for t in task_files:
                    task_name = t.filename
                    task_data = t.read().decode("utf-8")
                    task_id = insert_task(task_name, task_data, "user")
                    task.append(task_id)
                new_analysis_id = create_new_analysis(data, task, chosen_project_id, None)
                update_modified_date(chosen_project_id)
                app = current_app._get_current_object()
                computing_thread = threading.Thread(target=compute, args=(sock, "analysis", new_analysis_id, app, session['role'],))
                computing_thread.start()
                #compute(sock, "analysis", new_analysis_id)
                return render_template('look_analysis.html', analysis_data=get_analysis_data(new_analysis_id), analysis_task=get_analysis_task(new_analysis_id), user=session['user'], role=session['role'])
                #return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), analysis_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])

            
            if value == 'estimation_unary':
                data = request.form
                first_front = request.files['first_front'].read().decode("utf-8") 
                reference_set = request.files['reference_set'].read().decode("utf-8") 
                new_estimation_id = create_new_estimation(data, first_front, None, reference_set, chosen_project_id)
                update_modified_date(chosen_project_id)
                app = current_app._get_current_object()
                computing_thread = threading.Thread(target=compute, args=(sock, "estimation", new_estimation_id, app, session['role'],))
                computing_thread.start()
                #compute(sock, "estimation", new_estimation_id)
                return render_template('look_estimation.html', estimation_data=get_estimation_data(new_estimation_id), user=session['user'], role=session['role'])
                #return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), estimation_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
            
            if value == 'estimation_binary':
                data = request.form
                first_front = request.files['first_front'].read().decode("utf-8")
                second_front = request.files['second_front'].read().decode("utf-8")
                new_estimation_id = create_new_estimation(data, first_front, second_front, None, chosen_project_id)
                update_modified_date(chosen_project_id)
                app = current_app._get_current_object()
                computing_thread = threading.Thread(target=compute, args=(sock, "estimation", new_estimation_id, app, session['role'],))
                computing_thread.start()
                #compute(sock, "estimation", new_estimation_id)
                return render_template('look_estimation.html', estimation_data=get_estimation_data(new_estimation_id), user=session['user'], role=session['role'])
                #return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), estimation_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
        
        if 'cancel_button' in request.form:
            value = request.form['cancel_button']
            if value == 'calculation':
                return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), calculation_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
            if value == 'analysis':
                return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), analysis_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
            if value == 'estimation':
                return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), estimation_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])

        if 'delete_calculation' in request.form:
            calculation_id = request.form['delete_calculation']
            user_task = check_user_task("calculation", calculation_id)
            if (user_task):
                delete_task(user_task[0]['id'])
            delete_calculation(calculation_id)
            update_modified_date(chosen_project_id)
            return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
        
        if 'delete_analysis' in request.form:
            analysis_id = request.form['delete_analysis']
            user_task = check_user_task("analysis", analysis_id)
            if (user_task):
                for t in user_task:
                    delete_task(t['id'])
            delete_analysis(analysis_id)
            update_modified_date(chosen_project_id)
            return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), analysis_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
        
        if 'delete_estimation' in request.form:
            estimation_id = request.form['delete_estimation']
            delete_estimation(estimation_id)
            update_modified_date(chosen_project_id)
            return render_template('look_project.html', calculations=get_project_calculations(chosen_project_id), analyses=get_project_analyses(chosen_project_id), estimations=get_project_estimations(chosen_project_id), estimation_action=True, project_name=get_project_name(chosen_project_id), user=session['user'], role=session['role'])
       
        if 'show_calculation' in request.form:
            calculation_id = request.form['show_calculation']
            return render_template('look_calculation.html', calculation_data=get_calculation_data(calculation_id), user=session['user'], role=session['role'])
        
        if 'show_analysis' in request.form:
            analysis_id = request.form['show_analysis']
            return render_template('look_analysis.html', analysis_data=get_analysis_data(analysis_id), analysis_task=get_analysis_task(analysis_id), user=session['user'], role=session['role'])
        
        if 'show_estimation' in request.form:
            estimation_id = request.form['show_estimation']
            return render_template('look_estimation.html', estimation_data=get_estimation_data(estimation_id), user=session['user'], role=session['role'])


def create_new_project(data):
    model = project.ProjectModel(session['role'])
    project_name = data.get("name")
    project_description = data.get("description")
    user_id = session['user_id']
    model.insert_project(user_id, project_name, project_description)


def get_projects_list(user_id):
    """получение списка всех проектов пользователя"""
    model = project.ProjectModel(session['role'])
    result = model.get_projects(user_id)
    return result


def delete_project(project_id):
    model = project.ProjectModel(session['role'])
    model.delete_project(project_id)

def get_project_name(project_id):
    """получение названия проекта"""
    model = project.ProjectModel(session['role'])
    result = model.get_project_name(project_id)
    return result


def create_new_calculation(data, project_id, algorythm_parameters_separately):
    model = calculation.CalculationModel(session['role'])
    calculation_name = data.get("name")
    calculation_task = data.get("task")
    calculation_algorythm = data.get("algorythm")
    
    algorythm_parameters = str()
    task_parameters = str()

    if (data.get("algorythm_parameter") or algorythm_parameters_separately):
        algorythm_parameters_names_dictionary = get_algorythm_parameters_list(calculation_algorythm)
        algorythm_parameters_names = list()
        if (algorythm_parameters_separately):
            algorythm_parameters_values = algorythm_parameters_separately
        else:
            algorythm_parameters_values = data.getlist('algorythm_parameter')
        for i in algorythm_parameters_names_dictionary:
            algorythm_parameters_names.append(i['name'])
        for i in range(len(algorythm_parameters_names)):
            algorythm_parameters += algorythm_parameters_names[i] + "=" + algorythm_parameters_values[i] + ';'
        algorythm_parameters = algorythm_parameters[:-1]
    else:
        algorythm_parameters = "No parameters"
    print(algorythm_parameters)

    if (data.get("task_parameter")):
        task_parameters_names_dictionary = get_task_parameters_list(calculation_task)
        task_parameters_names = list()
        task_parameters_values = data.getlist('task_parameter')
        for i in task_parameters_names_dictionary:
            task_parameters_names.append(i['name'])
        for i in range(len(task_parameters_names)):
            task_parameters += task_parameters_names[i] + "=" + task_parameters_values[i] + ';'
        task_parameters = task_parameters[:-1]
    else:
        task_parameters = "No parameters"
    print(task_parameters)
    
    result = model.insert_calculation(project_id, calculation_name,
                             calculation_task, calculation_algorythm, algorythm_parameters, task_parameters)
    return result


def delete_calculation(calculation_id):
    model = calculation.CalculationModel(session['role'])
    model.delete_calculation(calculation_id)

def delete_analysis(analysis_id):
    model = analysis.AnalysisModel(session['role'])
    model.delete_analysis(analysis_id)


def get_project_calculations(project_id):
    """получение списка всех расчетов в проекте"""
    model = calculation.CalculationModel(session['role'])
    result = model.get_calculations(project_id)
    return result


def get_calculation_data(calculation_id, role=None):
    """получение информации о расчете"""
    if role:
        model = calculation.CalculationModel(role)
    else:
        model = calculation.CalculationModel(session['role'])
    result = model.get_calculation_data(calculation_id)
    return result


def get_project_analyses(project_id):
    """получение списка всех анализов в проекте"""
    model = analysis.AnalysisModel(session['role'])
    result = model.get_analyses(project_id)
    return result


def update_modified_date(project_id):
    """обновление даты модификации проекта"""
    model = project.ProjectModel(session['role'])
    result = model.update_modified_date(project_id)
    return result


def create_new_analysis(data, task, project_id, algorythm_parameters_separately):
    model = analysis.AnalysisModel(session['role'])
    analysis_name = data.get("name")
    analysis_task = task
    analysis_algorythm = data.get("algorythm")

    algorythm_parameters = str()

    if (data.get("algorythm_parameter") or algorythm_parameters_separately):
        algorythm_parameters_names_dictionary = get_algorythm_parameters_list(analysis_algorythm)
        algorythm_parameters_names = list()
        if (algorythm_parameters_separately):
            algorythm_parameters_values = algorythm_parameters_separately
        else:
            algorythm_parameters_values = data.getlist('algorythm_parameter')
        for i in algorythm_parameters_names_dictionary:
            algorythm_parameters_names.append(i['name'])
        for i in range(len(algorythm_parameters_names)):
            algorythm_parameters += algorythm_parameters_names[i] + "=" + algorythm_parameters_values[i] + ';'
        algorythm_parameters = algorythm_parameters[:-1]
    else:
        algorythm_parameters = "No parameters"
    print(algorythm_parameters)

    new_analysis_id = model.insert_analysis(project_id, analysis_name,
                                            analysis_algorythm, algorythm_parameters)
    model.insert_task_in_analysis(new_analysis_id, analysis_task)

    for t in analysis_task:
        if (data.get("t_" + t)):
            task_parameters_names_dictionary = get_task_parameters_list(t)
            task_parameters_names = list()
            task_parameters = str()

            task_parameters_values = data.getlist("t_" + t)

            for i in task_parameters_names_dictionary:
                task_parameters_names.append(i['name'])

            for i in range(len(task_parameters_names)):
                task_parameters += task_parameters_names[i] + "=" + task_parameters_values[i] + ';'
            
            task_parameters = task_parameters[:-1]
            model.insert_analysis_task_parameters(new_analysis_id, t, task_parameters)
        else:
            model.insert_analysis_task_parameters(new_analysis_id, t, "No parameters")

    return new_analysis_id

def get_analysis_data(analysis_id, role=None):
    """получение информации о анализе"""
    if role:
        model = analysis.AnalysisModel(role)
    else:
        model = analysis.AnalysisModel(session['role'])
    result = model.get_analysis_data(analysis_id)
    return result

def get_analysis_task(analysis_id, role=None):
    """получение задач из анализа"""
    if role:
        model = analysis.AnalysisModel(role)
    else:
        model = analysis.AnalysisModel(session['role'])
    result = model.get_analysis_task(analysis_id)
    return result


def get_project_estimations(project_id):
    """получение списка всех оценок в проекте"""
    model = estimation.EstimationModel(session['role'])
    result = model.get_estimations(project_id)
    return result

def create_new_estimation(data, first_front, second_front, reference_set, project_id):
    model = estimation.EstimationModel(session['role'])
    estimation_name = data.get("name")
    estimation_indicator = data.get("indicator")
    estimation_first_front = first_front
    estimation_second_front = second_front
    estimation_reference_set = reference_set
    result = model.insert_estimation(project_id, estimation_name,
                             estimation_indicator, estimation_first_front, estimation_second_front, estimation_reference_set)
    return result

def get_estimation_data(estimation_id, role=None):
    """получение информации о оценке"""
    if role:
        model = estimation.EstimationModel(role)
    else:
        model = estimation.EstimationModel(session['role'])
    result = model.get_estimation_data(estimation_id)
    return result

def delete_estimation(estimation_id):
    model = estimation.EstimationModel(session['role'])
    model.delete_estimation(estimation_id)

def get_algorythms_parameters():
    model = algorythm.AlgorythmModel(session['role'])
    result = model.get_algorythms_parameters()
    return result

def get_algorythm_parameters_list(algorythm_id):
    model = algorythm.AlgorythmModel(session['role'])
    result = model.get_algorythm_parameters_list(algorythm_id)
    return result

def get_algorythms():
    """получение списка алгоритмов"""
    model = algorythm.AlgorythmModel(session['role'])
    result = model.get_algorythms()
    return result

def get_tasks():
    """получение списка задач"""
    model = task.TaskModel(session['role'])
    result = model.get_tasks()
    return result

def get_tasks_parameters():
    model = task.TaskModel(session['role'])
    result = model.get_tasks_parameters()
    return result

def get_task_parameters_list(task_id):
    model = task.TaskModel(session['role'])
    result = model.get_task_parameters_list(task_id)
    return result

def get_indicators(type, role=None):
    """получение списка индикаторов"""
    if role:
        model = indicator.IndicatorModel(role)
    else:
        model = indicator.IndicatorModel(session['role'])
    result = model.get_indicators(type)
    return result

def insert_task(name, data, type):
    model = task.TaskModel(session['role'])
    new_task_id = model.insert_task(name, data, type)
    model.insert_task_parameter(new_task_id, "No parameters")
    return new_task_id

def delete_task(task_id):
    model = task.TaskModel(session['role'])
    model.delete_task(task_id)

def check_user_task(type, id):
    model = task.TaskModel(session['role'])
    result = model.check_user_task(type, id)
    return result

def update_calculation_results(id, approximation, indicators, role=None):
    if role:
        model = calculation.CalculationModel(role)
    else:
        model = calculation.CalculationModel(session['role'])
    model.update_results(id, approximation, indicators)

def update_estimation_results(id, indicator_results, role=None):
    if role:
        model = estimation.EstimationModel(role)
    else:
        model = estimation.EstimationModel(session['role'])
    model.update_results(id, indicator_results)

def update_analysis_results(id, results, role=None):
    if role:
        model = analysis.AnalysisModel(role)
    else:
        model = analysis.AnalysisModel(session['role'])
    model.update_results(id, results)

def compute(sock, type, id, app, role):
    print("Thread id = " + str(threading.get_ident()))
    if (type == "calculation"):
        indicators = list()
        with app.app_context():
            calculation_data = get_calculation_data(id, role)
            indicators_data = get_indicators("unary", role)
        for indicator in indicators_data:
            indicators.append(indicator['name'])
        data = {'type': type, 'id': id, 'task': calculation_data[0]['task_data'], 'task_name': calculation_data[0]['task_name'], 'algorythm': calculation_data[0]['algorythm'], 'algorythm_parameters': calculation_data[0]['algorythm_parameters'], 'task_parameters': calculation_data[0]['task_parameters'], 'indicators': indicators}
    elif (type == "estimation"):
        with app.app_context():
            estimation_data = get_estimation_data(id, role)
        data = {'type': type, 'id': id, 'first_front': estimation_data[0]['first_front'], 'second_front': estimation_data[0]['second_front'], 'indicator': estimation_data[0]['indicator_name']}
    elif (type == "analysis"):
        with app.app_context():
            analysis_data = get_analysis_data(id, role)
            task = get_analysis_task(id, role)
        task_name = list()
        task_data = list()
        task_parameters = list()
        for t in task:
            task_name.append(t['name'])
            task_data.append(t['data'])
            task_parameters.append(t['parameters'])
        data = {'type': type, 'id': id, 'task_name': task_name, 'task': task_data, 'task_parameters': task_parameters, 'algorythm': analysis_data[0]['algorythm'], 'algorythm_parameters': analysis_data[0]['algorythm_parameters']}
    sock.connect(('localhost', 55000))  # подключемся к серверному сокету
    sock.send(pickle.dumps(data))  # отправляем сообщение
    encoded_data = sock.recv(1048576)  # читаем ответ от серверного сокета
    decoded_data = pickle.loads(encoded_data)
    sock.close()  # закрываем соединение
    #time.sleep(2)
    print(decoded_data)
    if (type == "calculation"):
        with app.app_context():
            update_calculation_results(id, decoded_data['approximation'], decoded_data['indicators'], role)
    elif (type == "estimation"):
        with app.app_context():
            update_estimation_results(id, decoded_data, role)
    elif (type == "analysis"):
        with app.app_context():
            update_analysis_results(id, decoded_data, role)
    return