# Tests


- To run existing tests

```bash

(venv_sqlalchemy) ╭─niko@Nikolais-MacBook-Pro  ~/FLASK/basic_flask_prj  ‹tests*› 
╰─$ python manage.py test --coverage            
test_app_exists (test_basics.BasicsTestCase) ... ok
test_app_is_testing (test_basics.BasicsTestCase) ... ok
test_anonymous_user (test_role_model.UserModelTestCase) ... ok
test_roles_and_permissions (test_role_model.UserModelTestCase) ... --------------------------------------------------------------------------------
ok
test_password_setter (test_user_model.UserModelTestCase) ... --------------------------------------------------------------------------------
ok

Ran 5 tests in 0.253s

OK
Coverage Summary:
Name              Stmts   Miss Branch BrPart  Cover
---------------------------------------------------
app/__init__.py      29     15      0      0    48%
app/models.py       196    157     48      8    25%
---------------------------------------------------
TOTAL               225    172     48      8    27%


```


- HTML version: file:///Users/niko/FLASK/basic_flask_prj/tmp/coverage/index.html


- Uittests [tutorial](http://pythontesting.net/framework/unittest/unittest-introduction/)
- 
