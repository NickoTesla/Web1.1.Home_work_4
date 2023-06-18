from flask import Flask, render_template, request, redirect
from datetime import datetime
import json
import socket
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'storage'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        save_message(username, message)
        return redirect('/')
    return render_template('message.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404


def save_message(username, message):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        "username": username,
        "message": message
    }
    filename = f"{app.config['UPLOAD_FOLDER']}/data.json"
    with open(filename, 'a') as file:
        file.write(f'{timestamp}: {json.dumps(data)}\n')


def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 5000))

    while True:
        message, address = server_socket.recvfrom(1024)
        message = message.decode('utf-8')
        username, text = message.split(':')
        save_message(username.strip(), text.strip())


def run_flask():
    app.run(port=3000)


if __name__ == '__main__':
    socket_thread = threading.Thread(target=socket_server)
    flask_thread = threading.Thread(target=run_flask)

    socket_thread.start()
    flask_thread.start()
