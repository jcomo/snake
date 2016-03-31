from snake import *
import os

ENV = 'env'


@task
def bootstrap():
    """Bootstrap the virtualenv"""
    if not os.path.exists(ENV):
        sh('virtualenv -p python2.7 %s' % ENV)


@task(requires=['bootstrap'])
def install():
    """Install development dependencies"""
    sh('%s/bin/pip install -r requirements.txt' % ENV)


@namespace
def test():

    @task
    def current(test=''):
        """Run tests in current virtualenv"""
        sh('%s/bin/nosetests -s %s' % (ENV, test))

    @task
    def all():
        """Run tests for all support distributions"""
        sh('tox --skip-missing-interpreters')


@task
def upload():
    """Upload the current version to PyPI"""
    sh('rm -rf build dist')
    sh('python setup.py sdist bdist_wheel')
    sh('twine upload -u jcomo dist/*')
