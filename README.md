# Basic flask project

This is basic project using bluiprints that has a lot of boring boilerplate built in, the idea is to build project with most social application features already implemented to make it easier starting  new projects.

- currently following extensions are integrated:
  - flask_admin for authentication
  - flas_wtf for forms
  - flask_script for shell interaction
  - flask_moment for frontend dates
  - flask_bootsrap as frontend framework
  - flask_migrate for alembic migrations
  
 - following models are implemented:
   - users
   - roles
   - permissions

- following app functionality is implemented:
  - authentication
  - authorization
  - rest api 

### Getting started

```bash
# clone this project
pip install -r requirements.txt
python manage.py shell 
db.create_all()
python manage.py runserver
```
