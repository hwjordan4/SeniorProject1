from flask import Flask, render_template, request, session, redirect, url_for
from flask.ext.bcrypt import Bcrypt
import utilities
import amm_db
from datetime import date
import calendar

app = Flask(__name__)
app.debug = True
bcrypt = Bcrypt(app)
app.secret_key = ''

db = amm_db.AmmDB('')


@app.route('/', methods=['GET', 'POST'])
def main_page():
    session['userID'] = None

    if request.method == 'POST':
        if request.form.get('email', None) is not None:
            db.add_user(fn=request.form['first_name'], ln=request.form['last_name'], email=request.form['email'],
                        uname=request.form['username'], passwd=bcrypt.generate_password_hash(request.form['password']))
        elif request.form.get('username-login', None) is not None:
            data = db.get_user(uname=request.form['username-login'], exact=True)

            if len(data) > 0:
                if bcrypt.check_password_hash(data[0]['passwd'], request.form['password-login']):
                    user_id = data[0]['id']
                    session['user_id'] = user_id
                    return redirect(url_for('home'))

                else:
                    return render_template('MainPage.html', error='Username/Password is incorrect')
            else:
                return render_template('MainPage.html', error='Username/Password is incorrect')

    return render_template('MainPage.html')


@app.route('/home')
def home():
    if session.get('user_id', None) is None:
        return redirect(url_for('main_page'))
    else:
        user_info = db.get_user(session.get('user_id'))
        return render_template('home.html', user=user_info)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if session.get('user_id', None) is None:
        return redirect(url_for('main_page'))
    else:
        user_info = db.get_user(session.get('user_id'))
        if request.method == 'POST':
            response = 'Passwords do not match!'
            if request.form['password'] != request.form['c_password']:
                return render_template('profile.html', user=user_info, response=response, css_class='red-text')
            else:
                if request.form['password'] != '':
                    db.edit_user(session.get('user_id'), email=request.form['u_email'],
                             fname=request.form['fname'], lname=request.form['lname'],
                             passwd=bcrypt.generate_password_hash(request.form['password']),
                                 phone = request.form['phone'])
                else:
                    db.edit_user(session.get('user_id'), email=request.form['u_email'],
                             fname=request.form['fname'], lname=request.form['lname'],
                             passwd='', phone=request.form['phone'])


                if db.get_user(session.get('user_id')) == -1:
                    response = ''
                else:
                    user_info = db.get_user(session.get('user_id'))
                    response = 'Update made to profile!'

                return render_template('profile.html', response=response, css_class='green-text', user=user_info)
        else:
            return render_template('profile.html', user=user_info)


@app.route('/create_event', methods=['POST', 'GET'])
def create_event():
    if session.get('user_id', None) is None:
        return redirect(url_for('main_page'))
    user_info = db.get_user(session.get('user_id'))
    categories = db.get_activity_type()

    if request.method == 'POST':
        activity_name = request.form['activity-name']
        category = request.form['category']
        private = request.form['private']
        date = request.form['date']
        time = request.form['time']
        duration = request.form['duration']
        latitude = request.form['lat']
        longitude = request.form['lng']
        num_of_players = request.form['num-of-players']
        skill = request.form['skill-level']
        datetime = utilities.combine_datetime(date, time)

        db.add_activity(name=activity_name, category=category, datetime=datetime, duration=duration, latitude=latitude,
                        longitude=longitude, numplayers=num_of_players, skill=skill, private=private, leader=session.get
                        ('user_id'), available=1)

        redirect(url_for('home'))

    return render_template('create_event.html', key=utilities.get_maps_key(), user=user_info, categories=categories)


@app.route('/calender')
def calender():
    d = date.today()
    start_date = date(d.year, d.month, 1).weekday() + 1
    month = calendar.month_name[d.month]
    m_range = calendar.monthrange(d.year, d.month)
    end_date = m_range[1]

    ## Need to create a dictionary with the key being the day of the month its on as an integer
    ## Value can be string or array to handle on front end
    activities = {4: 'Soccer: 7:30', 21: 'Baseball - 6:30', 15: 'Chess Match', 2: 'Free Running'}
    keys = list(activities.keys())
    print(keys)

    return render_template('calender.html', user=' ', activity=activities, keys=keys,
                           current=d.day, start=start_date, date=d, month=month, end_date=end_date)

@app.route('/search', methods=['POST', 'GET'])
def search():
    if session.get('user_id', None) is None:
        return redirect(url_for('main_page'))
    user_info = db.get_user(session.get('user_id'))
    categories = db.get_activity_type()

    if request.method == 'POST':
        activity_name = request.form['activity-name']
        results = db.get_activity(name=activity_name)

        return render_template('SearchResultsPage.html', user=user_info, results=results, categories=categories)
    else:
        return render_template('SearchResultsPage.html', user=user_info, categories=categories)


@app.route('/rosters')
def rosters():
    if session.get('user_id', None) is None:
        return redirect(url_for('main_page'))
    user_info = db.get_user(session.get('user_id'))
    return render_template('RostersPage.html', user=user_info, count=1)


@app.route('/logout')
def logout():
    if session.get('user_id', None) is None:
        return redirect(url_for('main_page'))
    session.clear()
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    app.run()
