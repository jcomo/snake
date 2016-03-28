from snake import *
import os

ENV = 'env'


@task("Bootstrap the virtualenv")
def bootstrap():
    if not os.path.exists(ENV):
        sh('virtualenv -p python2.7 %s' % ENV)


@task("Install development dependencies")
def install():
    sh('%s/bin/pip install -r requirements.txt' % ENV)


@namespace
def test():

    @task("Run tests in current virtualenv")
    def current(test=''):
        sh('%s/bin/nosetests -s %s' % (ENV, test))

    @task("Run tests for all support distributions")
    def all():
        sh('tox')
