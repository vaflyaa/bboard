Web-service "BillBoard" as a pet-project. 

## Functional
- Admin site;
- User's profile;
- Email notifications;
- Post an ad;
- Left comments;
- Form search;
- Find potential buyer.

## Technologies used:
- MVC patern;
- ORM technology;
- Bootstrap4;
- DRF;
- PostreSQL.


<img width="1117" alt="main" src="https://user-images.githubusercontent.com/100959752/214544978-5dfb922c-8dac-4bfb-a096-fa2490cacc1c.png">

## Setup virtual environment
```
python -m venv .venv
source .venv/bin/activate
```
## Install packages
```
pip install -r requirements.txt
```
## Make migratons
```
python manage.py migrate
python manage.py makemigrations
```

## Run local server
```
python manage.py runserver
```
