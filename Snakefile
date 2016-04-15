from snake import *
import os

ENV_DIR = 'env'


@task
def bootstrap():
    """Bootstrap the virtualenv"""
    if not os.path.exists(ENV_DIR):
        sh('virtualenv -p python2.7 %s' % ENV_DIR)


@task(requires=['bootstrap'])
def install():
    """Install development dependencies"""
    sh('%s/bin/pip install -r requirements.txt' % ENV_DIR)


@namespace
def test():

    @task
    def current(test=''):
        """Run tests in current virtualenv"""
        sh('%s/bin/nosetests -s %s' % (ENV_DIR, test))

    @task
    def all():
        """Run tests for all support distributions"""
        sh('tox --skip-missing-interpreters')


@task
def upload():
    """Upload the current version to PyPI"""
    sh('rm -rf build dist')
    sh('python setup.py sdist bdist_wheel')
    sh('twine upload dist/*')
