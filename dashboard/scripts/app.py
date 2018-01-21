from flask import Flask, render_template, flash, redirect, url_for, request
from data import Jobs
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'mysql-host'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rallyteam'
app.config['MYSQL_DB'] = 'challenge'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

## Test used for no db case
Jobs = Jobs()

# Index
@app.route('/')
def home():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Jobs
@app.route('/jobs')
def jobs():
    # # Create cursor
    # cur = mysql.connection.cursor()

    # # Get jobs from db (jobs is the table name)
    # result = cur.execute("SELECT * FROM jobs")

    # jobs = cur.fetchall()

    # if result > 0:
    #     return render_template('jobs.html', jobs=Jobs)
    # else:
    #     msg = 'No Jobs Found'
    #     return render_template('jobs.html', msg=msg)
    # # Close connection
    # cur.close()

    ## Use faked data to test the page layout and route mechanism
    return render_template('jobs.html', jobs=Jobs)

#Single Job
@app.route('/job/<string:id>/')
def job(id):
    # # Create cursor
    # cur = mysql.connection.cursor()

    # # Get job
    # result = cur.execute("SELECT * FROM jobs WHERE id = %s", [id])

    # job = cur.fetchone()
    
    # similar_job_results = cur.execute("SELECT * FROM jobs WHERE (company = %s) AND (location = %s)", (job.company, job.location))
    # similar_jobs = similar_job_results.fetchall()

    # if similar_job_results>0:
    #     return render_template('job.html', job=job, similar_jobs=similar_jobs)
    # else:    
    #     return render_template('job.html', job=job)

    ## Use faked data to test the page layout and route mechanism
    job = Jobs[int(id)]
    similar_jobs = getsimilar(int(id))
    if len(similar_jobs)>0:
        return render_template('job.html', job=job, similar_jobs=similar_jobs)
    else:
        return render_template('job.html', job=job)
    

def getsimilar(job_id):
    """ Helper function to extract similar jobs for the faked data.
    """
    similar_jobs = []
    curr_job_company = Jobs[job_id]['company']
    curr_job_location = Jobs[job_id]['location']
    for i in range(len(Jobs)):
        if i is not job_id:
            job = Jobs[i]
            if job['company'] == curr_job_company \
                and job['location'] == curr_job_location:
                similar_jobs.append(job)
    return(similar_jobs)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


