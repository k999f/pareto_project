from flask import render_template, request, redirect, Blueprint, url_for, session
from ..auth import auth
from models import project, calculation, analysis, estimation, algorythm, task, indicator, users


administration_blueprint = Blueprint('administration_blueprint', __name__,
                           template_folder='templates')


@administration_blueprint.route('/', methods=['GET', 'POST'])
@auth.login_required
@auth.admin_rights_required
def administration():
    if request.method == 'POST':
        if 'create_button' in request.form:
            value = request.form['create_button']
            if value == 'user':
                return render_template('user_create_admin.html', roles=get_roles())
            
            if value == 'task':
                task_name = request.form['task_name']
                task_parameters = None
                if 'task_parameter' in request.form:
                    task_parameters = request.form.getlist('task_parameter')
                else:
                    task_parameters = "No parameters"
                print(task_parameters)
                insert_task(task_name, 'Standard task', 'standard', task_parameters)
                return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), task_action=True, user=session['user'], role=session['role'])

            if value == 'algorythm':
                algorythm_name = request.form['algorythm_name']
                algorythm_parameters = None
                if 'algorythm_parameter' in request.form:
                    algorythm_parameters = request.form.getlist('algorythm_parameter')
                else:
                    algorythm_parameters = "No parameters"
                print(algorythm_parameters)
                insert_algorythm(algorythm_name, algorythm_parameters)
                return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), algorythm_action=True, user=session['user'], role=session['role'])               

            if value == 'indicator':
                indicator_name = request.form['indicator_name']
                indicator_type = request.form['indicator_type']
                insert_indicator(indicator_name, indicator_type)
                return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), indicator_action=True, user=session['user'], role=session['role'])               

        elif 'edit_user' in request.form:
            user_id = request.form['edit_user']
            user_data = get_user_data(user_id)
            return render_template('edit_user.html', roles=get_roles(), id=user_data[0]['id'], login=user_data[0]['login'], password=user_data[0]['password'], role=user_data[0]['role'])

        elif 'save_edited_user' in request.form:
            data = request.form
            update_user(data)
            return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), user=session['user'], role=session['role'])

        elif 'save_button' in request.form:
            value = request.form['save_button']
            if value == 'user':
                data = request.form
                if data['password'] == data['repeat_password']:
                    exists, user_data = create_new_user(data)
                    if not exists:
                        #logger.info(session['name'] + " создал нового пользователя")
                        return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), user=session['user'], role=session['role'])
                    else:
                        return render_template('user_create_admin.html', user_data=user_data, roles=get_roles(), new_user_role=data['role'], already_exists=True,)
                else:
                    return render_template('user_create_admin.html', roles=get_roles(), mismatched_passwords=True, new_user_login=data['login'], new_user_role=data['role'])
        
        elif 'delete_task' in request.form:
            task_id = request.form['delete_task']
            delete_task(task_id)
            return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), task_action=True, user=session['user'], role=session['role'])        
        
        elif 'delete_algorythm' in request.form:
            algorythm_id = request.form['delete_algorythm']
            delete_algorythm(algorythm_id)
            return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), algorythm_action=True, user=session['user'], role=session['role'])        

        elif 'delete_indicator' in request.form:
            indicator_id = request.form['delete_indicator']
            delete_indicator(indicator_id)
            return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), indicator_action=True, user=session['user'], role=session['role'])        

        else:
            return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), user=session['user'], role=session['role'])        
    else:
        get_used_tasks()
        return render_template('administration_menu.html', users=get_users(), tasks=get_tasks(), algorythms=get_algorythms(), indicators=get_all_indicators(), user=session['user'], role=session['role'])

def get_users():
    model = users.UsersModel(session['role'])
    result = model.get_users()
    return result

def get_user_data(user_id):
    model = users.UsersModel(session['role'])
    result = model.get_user_data(user_id)
    return result

def get_tasks():
    """получение списка задач"""
    model = task.TaskModel(session['role'])
    tasks = model.get_tasks()
    used_tasks = get_used_tasks()
    result = list()
    for t in tasks:
        if (t['id'] in used_tasks):
            t['is_used'] = True
            result.append(t)
        else:
            t['is_used'] = False
            result.append(t)
    print(result)
    return result

def get_algorythms():
    """получение списка алгоритмов"""
    model = algorythm.AlgorythmModel(session['role'])
    algorythms = model.get_algorythms()
    used_algorythms = get_used_algorythms()
    result = list()
    for a in algorythms:
        if (a['id'] in used_algorythms):
            a['is_used'] = True
            result.append(a)
        else:
            a['is_used'] = False
            result.append(a)
    print(result)
    return result

def get_all_indicators(role=None):
    """получение списка индикаторов"""
    if role:
        model = indicator.IndicatorModel(role)
    else:
        model = indicator.IndicatorModel(session['role'])
    unary_indicators = model.get_indicators("unary")
    for i in unary_indicators:
        i['type'] = "unary"
    binary_indicators = model.get_indicators("binary")
    for i in binary_indicators:
        i['type'] = "binary"
    indicators = unary_indicators + binary_indicators
    used_indicators = get_used_indicators()
    result = list()
    for i in indicators:
        if (i['id'] in used_indicators):
            i['is_used'] = True
            result.append(i)
        else:
            i['is_used'] = False
            result.append(i)
    print(result)
    return result

def get_roles():
    model = users.UsersModel(session['role'])
    result = model.get_roles()
    return result

def create_new_user(data):
    model = users.UsersModel(session['role'])
    user_login = data.get("login")
    user_password = data.get("password")
    user_role = data.get("role")
    created = model.insert_users(user_login, user_password, user_role)
    if created == 'None':
        return True, {'login': user_login,
                      'password': user_password,
                      'role': user_role}
    else:
        return False, {}

def update_user(data):
    model = users.UsersModel(session['role'])
    user_id = data.get("id")
    user_password = data.get("password")
    user_role = data.get("role")
    model.update_users(user_id, user_password, user_role)

def get_used_tasks():
    result = list()
    model = task.TaskModel(session['role'])
    calculation_tasks = model.get_calculation_used_tasks()
    analysis_tasks = model.get_analysis_used_tasks()
    for c in calculation_tasks:
        result.append(c['id'])
    for a in analysis_tasks:
        result.append(a['id'])
    result = sorted(list(set(result)))
    return result

def delete_task(task_id):
    model = task.TaskModel(session['role'])
    model.delete_task(task_id)

def insert_task(name, data, type, parameters):
    model = task.TaskModel(session['role'])
    new_task_id = model.insert_task(name, data, type)
    if (parameters == "No parameters"):
        model.insert_task_parameter(new_task_id, "No parameters")
    else:
        for parameter in parameters:
            model.insert_task_parameter(new_task_id, parameter)
    return new_task_id

def get_used_algorythms():
    result = list()
    model = algorythm.AlgorythmModel(session['role'])
    calculation_algorythms = model.get_calculation_used_algorythms()
    analysis_algorythms = model.get_analysis_used_algorythms()
    for c in calculation_algorythms:
        result.append(c['id'])
    for a in analysis_algorythms:
        result.append(a['id'])
    result = sorted(list(set(result)))
    return result

def insert_algorythm(name, parameters):
    model = algorythm.AlgorythmModel(session['role'])
    new_algorythm_id = model.insert_algorythm(name)
    if (parameters == "No parameters"):
        model.insert_algorythm_parameter(new_algorythm_id, "No parameters")
    else:
        for parameter in parameters:
            model.insert_algorythm_parameter(new_algorythm_id, parameter)
    return new_algorythm_id

def delete_algorythm(algorythm_id):
    model = algorythm.AlgorythmModel(session['role'])
    model.delete_algorythm(algorythm_id)

def get_used_indicators():
    result = list()
    model = indicator.IndicatorModel(session['role'])
    indicators = model.get_used_indicators()
    for i in indicators:
        result.append(i['id'])
    result = sorted(list(set(result)))
    return result

def insert_indicator(name, type):
    model = indicator.IndicatorModel(session['role'])
    result = model.insert_indicator(name, type)
    return result

def delete_indicator(indicator_id):
    model = indicator.IndicatorModel(session['role'])
    model.delete_indicator(indicator_id)