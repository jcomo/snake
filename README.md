# snake

Build script utility for Python. Ported from the popular Ruby tool, [Rake](https://github.com/ruby/rake).

## Motivation

Rake is a tried and true build tool for the Ruby community and there are many of us in the Python community who use it to automate steps of our builds or aspects of our development environments.
What Rake really lacks when using it with a Python project is the ability to hook into Python code within the project. Usually the pattern is to create a python script and then expose it with a Rake task, which is a lot of overhead for a tool whose goal is to reduce overhead.
Snake is meant to be a comparable tool to Rake with familiar syntax and concepts that allows Python developers to write automation tasks in the same language of their project.

Snake aims to maintain a similar goal to Rake, which is to reduce the overhead to add automation to a project. It does this by providing terse, straightforward syntax in a flexible, yet simple tool.

## Installation

First, install Snake. It is recommended to install it to your system Python instead of a local Python installation since it is meant to be a global exectuable.
Use a local installation if you need a specific version.

```
pip install snake
```

## Usage

Similar to Rake, Snake uses a manifest file called the `Snakefile`, which contains definitions for your build tasks.

```python
from snake import *

@task("Say hello")
def hello(name='World'):
    sh('echo Hello, %s!' % name)
```

From the directory containing your `Snakefile`, you can run the `hello` task using

```
snake hello  # echos "Hello, World!"
snake hello name=Github  # echos "Hello, Github!"
```

### Defining Tasks

To define a task, decorate a function with `@task(description)`.
The description is a quick blurb explaining the goal of the task.

Functions that become tasks can accept keyword arguments that will be specified on the command line.
However, keyword arguments supplied to the function via Snake will always be strings.
The function itself is not modified in any way by `@task` so the function can be called normally everywhere else in the program.

Namespaces can also be used to group sets of related tasks by using the `@namespace` decorator.
Note that the decorator accepts no parameters. The function that it decorates must also not accept any parameters.

Below is an example defining regular tasks, and namespaced tasks.

```python
from snake import *

@task("Bootstraps the environment")
def bootstrap():
    sh('echo Bootstrapping...')

@namespace
def build():

    @task("Builds the tools")
    def tools():
        sh('echo Building the tools')

    @task("Builds the application")
    def app():
        sh('echo Building the application')
```

### Listing Tasks

To list the available tasks, use `snake -T`.
The output will consist of all available tasks and their respective descriptions.

Here is example output using the `Snakefile` from the previous section.

```
$ snake -T

bootstrap        # Bootstraps the environment
build:app        # Builds the tools
build:tools      # Builds the application
```

## Development Setup

To use your dev version of snake, you will first need to install development dependencies and wire up the development version of the script.
From inside the top level snake development directory, run

```
alias snakedev="PYTHONPATH=`pwd` `pwd`/bin/snake"
snakedev bootstrap install
```

You could instead alias to `snake`, but remember to `unalias` when you are done developing in order to switch back to the installed version.
