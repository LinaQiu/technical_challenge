# [Answers to Analysis Q1 & Q2](https://github.com/LinaQiu/technical_challenge/tree/master/analysis_q1_q2)

# Installation

To run the scripts, your computer needs:

- [Python 3](https://python.org)
- [Pip Package Manager](https://pypi.python.org/pypi)
- [Docker](https://www.docker.com/)
- [Docker Compose 3.x](https://docs.docker.com/compose/compose-file/)

# Scraper

Career sites scraped:
- [Google Career](https://careers.google.com/jobs)
- [Microsoft Career, Students and graduates](https://careers.microsoft.com/students/apply)

## Running the scrapers

- First, navigate to folder `scraper`.

```bash
docker-compose up –d
docker exec –it scraper bash
```

- Then, you will be inside the docker container, called `scraper`. The scripts are volumed to a folder also called `scripts` under the container.

```bash
cd scripts
python google_scraper.py
python microsoft_scraper.py
```

- Crawling results are stored in JSON format. 
	- Results from Google contains the following things: `title, company, location, description-section, description-section text, description-section text with-benefits.`
	- Results from Microsoft contains the following things: `Focus area, Education level, Job type, company, Location, description.`
- Now, run a script (`reformat_json.py`) to convert the above raw results to a text file with the same format as the database table (`jobs` in db `challenge`). 
	- For Google: combined all `description-section*` text as a single item, `description`. 
	- For Microsoft: combined `Focus area, Education level, Job type` together, as job `title`. 
		- Note: The pop up window of job details from Microsoft mixed several jobs together, and does not differntiate each sub job in their source. Hence, I was not able to fetch the titles for each sub job, and therefore decided to combine the three items together as the title.
- Name the text file as `all_jobs.txt`, copy to the folder called `data` under `dashboard`, for the later use of loading to the database table. 

- Navigate to folder `dashboard`:

```bash
docker-compose up –d
docker exec –it db bash	# Start the MySQL container
```

- Run the following commands to create the database `challenge` under MySQL container: 
```bash
### Inside the container, first we need to log in to mysql server
mysql -p [type the password for root user]

### Now, we will be in mysql server. 
CREATE DATABASE challenge;
USE DATABASE challenge

CREATE TABLE jobs (id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT, 
	company VARCHAR(255), title VARCHAR(255), location(255), description TEXT, primary key (id));

### Take a look at the table
DESCRIBE jobs;

### Load the all_jobs.txt to the table
LOAD DATA LOCAL INFILE '/var/lib/mysql/all_jobs.txt' INTO TABLE jobs;
```

- MySQL table format:
```
	| id          | smallint(5) unsigned | NO   | PRI | NULL    | auto_increment |
	| company     | varchar(255)         | YES  |     | NULL    |                |
	| title       | varchar(255)         | YES  |     | NULL    |                |
	| location    | varchar(255)         | YES  |     | NULL    |                |
	| description | text                 | YES  |     | NULL    |                |

```

# Job dashboard

Simple application to present jobs scraped from Google and Microsoft.
  - [master branch](https://github.com/LinaQiu/technical_challenge): job dashboard tested with faked data, with code interacting with mysql database commented out. 
  - [mysqlversion branch](https://github.com/LinaQiu/technical_challenge/tree/mysqlversion): job dashboard tested with actual job data stored in mysql, while not working yet, due to database access issue, with code for faked data testing commented out. 

```bash
### Start the web container interactively, running python3, with flask.
docker exec –it web bash	
```

### Running the app

```bash
cd scripts
python app.py
```

- Open the link `http://0.0.0.0:5000` at your local machine. 

### Limitations: 
- Similar jobs are defined as any jobs from the same company, and at the same location. 
  - Ideally, to find similar jobs among two companies, we should do cluster analysis. For example, we could take job description text for all jobs, and apply k-means, to cluster all jobs to several category (text document clustering). 
  - Afterwards, we could have another data column in the db, to record the job category. However, due to time limitation, I did not get to finish this part.  
- The app is not fully tested yet, due to technical difficulties regarding accessing the database from outside the mysql container, and connecting to the mysql server at local machine right the installation.
  - Even though both my web app container mysql container are under the same default network, the web app container still can't access the database from mysql container. This is probably related to the sensitive permission settings for database server. 
  - While many people had the same issue, and I read all their questions and potential solutions other people provided, I was still not able to figure out how to config the containers/database, to make it accessible. 
- Another thing need to improve is to make the main dashbord (presenting the job list) pagination, to adapt to the long list of jobs we have. 

