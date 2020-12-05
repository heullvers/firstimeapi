from threading import Timer
from flask import Flask

app = Flask(__name__)
DATA = "data"
atualizar = True

def update_data(interval):
    Timer(interval, update_data, [interval]).start()
    global DATA
    DATA = getDados()
    atualizar = True
    

# update data every second
update_data(1)

@app.route("/")
def index():
    return DATA

if __name__ == "__main__":
    app.run(debug=True)