## Huddl, a meetup planning app

Our friend group often struggled to plan out hangouts due to various problems - somebody lived too far away, somebody was always busy, somebody was always broke, the list goes on and on. 

We wanted to make something that could make it easier to bring people together and touch grass :)

Huddl allows users to form "groups" where they can organize hangouts based on attributes of members in said groups. They can input various attributes, which makes it much easier to planners to select activities and the like. It also allows for ease of scheduling and notification!

## The Backend Server

This project is the backend server for Huddl, built using DJango. 

### Quickstart

* Install required libraries in `requirements.txt`
* Navigate to `settings.py` and set `ALLOWED_HOSTS` to include the domain the server is hosted on, `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` to domains the frontend is hosted on
* Run `python manage.py migrate` to create a database
* Run `python manage.py createsuperuser` and create an administrator
* Use `python manage.py runserver` to run the server!
* Set up [the frontend server](https://github.com/Trentiumz/Huddl-Frontend)