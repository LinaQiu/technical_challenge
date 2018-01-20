# Installation

To run the scripts, your computer needs:

- [Python 3](https://python.org)
- [Pip Package Manager](https://pypi.python.org/pypi)
- [Docker](https://www.docker.com/)

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
- Now, we will run a script to convert the above raw results to a text file with the same format as our database table (`jobs` in db `challenge`). 
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
LOAD DATA LOCAL INFILE '/var/lib/mysql-files/all_jobs.txt' INTO TABLE jobs;
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

Simple application to present jobs scraped from Google and Microsoft

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

- Note: 
	- Similar jobs are defined as any jobs from the same company, and at the same location. 
	- The app is not fully tested yet, due to technical difficulty regarding accessing the database from outside the mysql container. 

