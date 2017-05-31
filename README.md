# Basic flask project

This is basic [Flask](http://flask.pocoo.org/) project using blueprint that has a lot of boring boilerplate built in, the idea is to build project with most social application features already implemented or at leas have single example to make it easier starting  new projects.

- currently following extensions are integrated:
  - flask_admin for authentication
  - flas_wtf for forms
  - flask_script for shell interaction
  - flask_moment for frontend dates
  - flask_bootsrap as frontend framework
  - flask_migrate for alembic migrations
  
 - implemented models:
   - users
   - roles
   - permissions

- following app functionality is implemented:
  - authentication
  - authorization
  - rest api 
  
### Configuration `config.py`
- Main db is Postgresql , sqlite is not fully supports all the features but can be used for basic setup

```python
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                               'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/{}'.format(Config.PROJECT_NAME.lower())
```

### Getting started

```bash
# clone this project
pip install -r requirements.txt
python manage.py shell 
db.create_all()
╰─$ python manage.py runserver
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!

```
