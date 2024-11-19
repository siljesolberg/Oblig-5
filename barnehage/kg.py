from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from kgcontroller import (form_to_object_soknad,
                          insert_soknad, commit_all,
                          select_alle_barnehager,
                          select_alle_soknader, get_all_data)

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'  # nødvendig for session


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)


@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        sd = request.form
        print(sd)
        log = insert_soknad(form_to_object_soknad(sd))
        print(log)
        session['information'] = sd
        return redirect(url_for('svar'))  # [1]
    else:
        return render_template('soknad.html')


@app.route('/svar')
def svar():
    information = session['information']
    return render_template('svar.html', data=information)


@app.route('/commit')
def commit():
    commit_all()
    information = get_all_data()
    return render_template('commit.html', data=information)


@app.route('/soknader')
def soknader():
    real_data = select_alle_soknader()
    print("Debug: Current state of soknader data:", real_data)
    return render_template('soknader.html', soknader=real_data)


@app.route('/statistikk')
def statistikk():

    return render_template('statistikk.html')
