from flask import Flask, render_template, flash, redirect, url_for, request
# from data import Jobs
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rallyteam'
app.config['MYSQL_DB'] = 'challenge'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

## Test used for no db case
# Jobs = Jobs()

# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Jobs
@app.route('/jobs')
def jobs():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get jobs from db (jobs is the table name)
    result = cur.execute("SELECT * FROM jobs")

    jobs = cur.fetchall()

    if result > 0:
        return render_template('jobs.html', jobs=Jobs)
    else:
        msg = 'No Jobs Found'
        return render_template('jobs.html', msg=msg)
    # Close connection
    cur.close()


#Single Job
@app.route('/job/<string:id>/')
def job(id):
	return render_template('job.html')
    # Create cursor
    cur = mysql.connection.cursor()

    # Get job
    result = cur.execute("SELECT * FROM jobs WHERE id = %s", [id])

    job = cur.fetchone()
    
    SELECT expressions_and_columns FROM table_name
	[WHERE some_condition_is_true]
	[ORDER BY some_column [ASC | DESC]]
	[LIMIT offset, rows]

    similar_job_results = cur.execute("SELECT * FROM jobs WHERE (company = %s) AND (location = %s)", ([job.company], [job.location]))

    return render_template('job.html', job=job, similar_jobs=similar_jobs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


