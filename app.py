import os.path

from flask import Flask, render_template, request, redirect
from datetime import datetime
import json
import socket
import threading


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'storage'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        with socket.socket() as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(json.dumps({'username': username, 'message': message}).encode())
        return redirect('/')
    if request.method == "GET":
        return render_template('message.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404


def save_message(data):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    messages = json.loads(data.decode())
    username = messages['username']
    message = messages['message']
    data = {
        "username": username,
        "message": message
    }
    filename = f"{app.config['UPLOAD_FOLDER']}/data.json"
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({}, file)

    with open(filename, "r") as reader:
        history_data = json.load(reader)
        history_data.update({timestamp: data})

    with open(filename, 'w') as file:
        json.dump(history_data, file, indent=4, ensure_ascii=False)


def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((SERVER_IP, SERVER_PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            with conn:
                try:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        save_message(data)
                        print('Data was received')
                except KeyboardInterrupt:
                    print("Socket server stopped")
                    break
                except Exception as e:
                    print(f"Error in socket server: {e}")


def run_flask():
    app.run(port=3000)


if __name__ == '__main__':
    socket_thread = threading.Thread(target=socket_server)
    flask_thread = threading.Thread(target=run_flask)
    # run_flask()
    socket_thread.start()
    flask_thread.start()
