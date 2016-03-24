from snake import *

@task("Does something cool")
def something(name):
    sh('echo Hello %s' % name)

