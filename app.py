from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        # Тут можна додати логіку для обробки повідомлення
        return redirect('/')
    return render_template('message.html')


if __name__ == '__main__':
    app.run()
