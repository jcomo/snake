from snake import *

import os


@task("Bootstrap the virtualenv")
def bootstrap():
    if not os.path.exists('env'):
        sh('virtualenv -p python2.7 env')


@task("Install development dependencies")
def install():
    sh('env/bin/pip install -r requirements.txt')
