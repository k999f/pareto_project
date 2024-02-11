from flask import render_template, request, session, redirect, Blueprint, current_app, url_for
from models import users
from DBCM import UseDatabase
from functools import wraps
# from logger import logger, log_decorator


auth_blueprint = Blueprint('auth_blueprint', __name__,
                           template_folder='templates')
logout_blueprint = Blueprint('logout_blueprint', __name__)


@auth_blueprint.route('/', methods=['GET', 'POST'])
# @log_decorator
def authorization():
    if 'login_button' in request.form:
        result = []
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            with UseDatabase(current_app.config['db']['auth']) as cursor:
                cursor.execute("""SELECT role, id
                                        FROM users
                                        WHERE login='%s'
                                        AND password='%s'""" % (login, password))
                schema = ['role', 'user_id']
                for con in cursor.fetchall():
                    result.append(dict(zip(schema, con)))
            if len(result) > 0:
                session['role'] = result[0]['role']
                session['user_id'] = result[0]['user_id']
                session['user'] = login
                # logger.info(session['name'] + " вошёл в систему")
                return redirect(url_for('main_blueprint.main'))
            else:
                return render_template('auth.html', status='bad')
        else:
            return render_template('auth.html', status='bad')
    elif 'registration_button' in request.form:
        return render_template('user_create.html', user_data={}, already_exists=False)
    elif 'save_new_user' in request.form:
        data = request.form
        if data['password'] == data['repeat_password']:
            exists, user_data = create_new_user(data)
            if not exists:
                #logger.info(session['name'] + " создал нового пользователя")
                return render_template('auth.html', new_user_login=data['login'])
            else:
                return render_template('user_create.html', user_data=user_data, already_exists=True)
        else:
            return render_template('user_create.html', mismatched_passwords=True, new_user_login=data['login'])
    else:
        return render_template('auth.html')


def create_new_user(data):
    model = users.UsersModel('auth')
    user_login = data.get("login")
    user_password = data.get("password")
    user_role = 'client'
    created = model.insert_users(user_login, user_password, user_role)
    if created == 'None':
        return True, {'login': user_login,
                      'password': user_password,
                      'role': user_role}
    else:
        return False, {}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth_blueprint.authorization'))
        return f(*args, **kwargs)
    return decorated_function


def admin_rights_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['role'] != 'admin':
            return render_template('access_error.html', user=session['user'], role=session['role'])
        return f(*args, **kwargs)
    return decorated_function


@logout_blueprint.route('/', methods=['GET'])
@login_required
def logout():
    # logger.info(session['name'] + " вышел из системы")
    session.pop('role')
    session.pop('user_id')
    session.pop('user')
    return redirect(url_for('auth_blueprint.authorization'))
