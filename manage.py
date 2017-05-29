
#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Permission
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    # turns on test coverage
    import coverage

    # The branch=True option enables branch coverage analysis,
    # which, in addition to tracking which lines of code execute,
    # checks whether for every conditional both the True and False cases have executed.
    # The include option is used to limit coverage analysis to the files that are inside
    # the application package, which is the only code that needs to be measured.Without the include
    # option, all the extensions installed in the virtual environment and the code
    # for the tests itself would be included in the coverage reports
    # and that would add a lot of noise to the report.
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@manager.command
def test(coverage=False):
    """
    Adds command to run Unit tests with "coverage" boolean option.

    Flask-Script derives the name of the option from the argument name
    and passes True or False to the function accordingly.

    :param coverage:
    :return:
    """

    # Set the FLASK_COVERAGE env var on and restart the script
    # .In the second run, the top of the script finds that the
    # environment variable is set and turns  on coverage from the start.
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print "Coverage Summary:"
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission)

manager.add_command(
    "shell", Shell(make_context=make_shell_context))

manager.add_command(
    'db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
