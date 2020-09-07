from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return "<h1>Deployed update<h1>"
@app.route('/about')
def about():
    return render_template("/htmls/test.html")
if __name__ == '__main__':
    app.run(debug=True)

