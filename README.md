# snake [![Build Status](https://travis-ci.org/jcomo/snake.svg?branch=master)](https://travis-ci.org/jcomo/snake)

Build script utility for Python.
Ported from the popular Ruby tool, [Rake](https://github.com/ruby/rake).
Still very much a work in progress.

## Motivation

Rake is a tried and true build tool for the Ruby community and there are many of us in the Python community who use it to automate steps of our builds or aspects of our development environments.
What Rake really lacks when using it with a Python project is the ability to hook into Python code within the project. Usually the pattern is to create a python script and then expose it with a Rake task, which is a lot of overhead for a tool whose goal is to reduce overhead.
Snake is meant to be a comparable tool to Rake with familiar syntax and concepts that allows Python developers to write automation tasks in the same language of their project.

Snake maintains a similar goal of Rake, which is to reduce the overhead to add automation to a project. It does this by providing terse, straightforward syntax in a flexible, yet simple DSL.

## Installation

First, install Snake. It is recommended to install it to your system Python instead of a local Python installation since it is meant to be a global exectuable.
Use a local installation if you need a specific version.

```
pip install pyrake
```

## Usage

Similar to Rake, Snake uses a manifest file called the `Snakefile`, which contains definitions for your build tasks.

```python
from snake import *

@task
def hello(name='World'):
    """Say hello"""
    sh('echo Hello, %s!' % name)
```

From the directory containing your `Snakefile`, you can run the `hello` task using

```sh
snake hello  # echos "Hello, World!"
snake hello name=Github  # echos "Hello, Github!"
```

### Defining Tasks

To define a task, decorate a function with `@task(description)`.
The description is a quick blurb explaining the goal of the task.

Functions that become tasks can accept keyword arguments that will be specified on the command line.
However, keyword arguments supplied to the function via Snake will always be strings.
The function itself is not modified in any way by `@task` so the function can be called normally everywhere else in the program.

Dependeny tasks can be defined with the `requires` keyword arg to `@task`.
It accepts a list of strings where each string is the label of another task.
Task dependencies are resolved from left to right.
In the following example, executing the `install` task will always cause `bootstrap` to be executed first.

Namespaces can also be used to group sets of related tasks by using the `@namespace` decorator.
Note that the decorator accepts no parameters. The function that it decorates must also not accept any parameters.

A default task can be defined by setting `default` to a string corresponding to the name of the task function in the `Snakefile`.

Here we define regular tasks, tasks with dependencies, and task namespaces.

```python
from snake import *

default = 'build:tools'


@task
def bootstrap():
    """Bootstraps the environment"""
    sh('echo Bootstrapping...')


@task(requires=['bootstrap'])
def install():
    """Installs dependencies"""
    sh('echo Installing...')


@namespace
def build():

    @task
    def tools(typ='core'):
        """Builds the tools"""
        sh('echo Building the %s tools' % typ)

    @task
    def app(target):
        """Builds the application"""
        sh('echo Building the application for %s' % target)
```

### Listing Tasks

To list the available tasks, use `snake -T`.
The output will consist of all available tasks and their respective descriptions.

Here is example output using the `Snakefile` from the previous section.

```
$ snake -T

snake bootstrap                  # Bootstraps the environment
snake install                    # Installs dependencies
snake build:app target={target}  # Builds the tools
snake build:tools [typ=core]     # Builds the application
```

## API Reference

### `@task(requires=None)`

Decorates a function that then exposes it as a task to be run.
The name of the function becomes the name of the task.
The `requires` parameter, if specified, is a list of strings where each string is the name of a task that this one depends on.

### `@namespace`

Decorates a function so that it exposes a task namespace.
The name of the function becomes the name of the namespace.
Tasks and nested namespaces can be defined in the namespace and will be called as `namespace:task`.

### `sh(command, silent=False)`

Runs a shell command.
If silent is not specified, an exception will be raised if the resulting status of the command is nonzero.

### `ENV`

A dict that gives you access to environment variables.
It has a special property that accessing by key using brackets will not raise a `KeyError` but will return `None` instead.
