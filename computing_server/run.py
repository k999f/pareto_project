import socket
import pickle
import time
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
# связываем сокет с портом, где он будет ожидать сообщения
sock.bind(('', 55000))
sock.listen(10)  # указываем сколько может сокет принимать соединений
print('Computing server is running, press CTRL+C to stop')

def compute_calculation(id, algorythm, algorythm_parameters, task_parameters, task, task_name, indicators_list, conn):
    # print("Calculation received\n" + "id: " + id + ";", "algorythm: " + algorythm + ";", "task: " + task_name + ";", "indicators: " + str(indicators_list))
    print("Calculation received, id = " + id)
    if (algorythm_parameters == "No parameters"):
        algorythm_parameters = "no parameters"
    if (task_parameters == "No parameters"):
        task_parameters = "no parameters"
    approximation = "Approximation for task: " + task_name + "\nTask parameters: " + task_parameters + "\nUsed algorythm: " + algorythm + "\nAlgorythm parameters: " + algorythm_parameters + "\nResults:"
    indicators = "Indicators for task: " + task_name
    for indicator in indicators_list:
        indicators += "\n" + indicator + " = "
    results = {'approximation': approximation, 'indicators': indicators}
    time.sleep(6)
    conn.send(pickle.dumps(results))
    return

def compute_estimation(id, first_front, second_front, indicator, conn):
    # print("Estimation received\n" + "id: " + id + ";", "indicator: " + indicator)
    print("Estimation received, id = " + id)
    results = {}
    if not second_front:
        results = "Unary indicator: " + indicator
    else:
        results = "Binary indicator: " + indicator
    time.sleep(6)
    conn.send(pickle.dumps(results))
    return

def compute_analysis(id, algorythm, algorythm_parameters, task, task_name, task_parameters, conn):
    # print("Analysis received\n" + "id: " + id + ";", "algorythm: " + algorythm + ";", "task: " + str(task_name))
    print("Analysis received, id = " + id)
    if (algorythm_parameters == "No parameters"):
        algorythm_parameters = "no parameters"
    results = "Analysis using algorythm: " + algorythm + "\nAlgorythm parameters: " + algorythm_parameters
    results += "\nWith tasks:"
    for i in range(len(task_name)):
        if (task_parameters[i] == "No parameters"):
            task_parameters[i] = "no parameters"
        results += "\n" + task_name[i] + ", parameters: " + task_parameters[i]
    time.sleep(6)
    conn.send(pickle.dumps(results))
    return

while True:
    conn, addr = sock.accept()  # начинаем принимать соединения
    print('connected:', addr)  # выводим информацию о подключении
    results = {}
    encoded_data = conn.recv(1048576)  # принимаем данные от клиента, по 1 мб
    decoded_data = pickle.loads(encoded_data)
    if (decoded_data['type'] == 'calculation'):
        computing_thread = threading.Thread(target=compute_calculation, args=(decoded_data['id'], decoded_data['algorythm'], decoded_data['algorythm_parameters'], decoded_data['task_parameters'], decoded_data['task'], decoded_data['task_name'], decoded_data['indicators'], conn,))
        computing_thread.start()
        #compute_calculation(decoded_data['id'], decoded_data['algorythm'], decoded_data['task'], decoded_data['task_name'], decoded_data['indicators'], conn)
    elif (decoded_data['type'] == 'estimation'):
        computing_thread = threading.Thread(target=compute_estimation, args=(decoded_data['id'], decoded_data['first_front'], decoded_data['second_front'], decoded_data['indicator'], conn,))
        computing_thread.start()
        #compute_estimation(decoded_data['id'], decoded_data['first_front'], decoded_data['second_front'], decoded_data['indicator'], conn)
    elif (decoded_data['type'] == 'analysis'):
        computing_thread = threading.Thread(target=compute_analysis, args=(decoded_data['id'], decoded_data['algorythm'], decoded_data['algorythm_parameters'], decoded_data['task'], decoded_data['task_name'], decoded_data['task_parameters'], conn,))
        computing_thread.start()
        #compute_analysis(decoded_data['id'], decoded_data['algorythm'], decoded_data['task'], decoded_data['task_name'], conn)
    # в ответ клиенту отправляем сообщение в верхнем регистре
    #conn.send(pickle.dumps(results))
conn.close()  # закрываем соединение
