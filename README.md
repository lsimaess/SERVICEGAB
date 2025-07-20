# ServiceGab

A Flask web application that connects service requesters and workers in Gabon.

## Features

- Worker and Requester registration
- Admin dashboard for approval and job assignment
- Service request lifecycle: pending → assigned → completed/cancelled
- PostgreSQL + SQLAlchemy ORM
- Deployed on AWS EC2 (Gunicorn + Nginx)

## Tech Stack

- Python (Flask)
- PostgreSQL (AWS RDS)
- Gunicorn + Nginx (Production)
- Bootstrap 5 (Frontend)

## Running Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask run
# SERVICEGAB
MARKETPALCE FOR SERVICE TO CONNECT TO SERVICE PROVIDER
