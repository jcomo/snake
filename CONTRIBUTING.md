# Contributing to Snake

Contributions are welcome and applauded.

## How to Submit Changes

We ask that you first open an issue if it is going to be a larger change so that there can be some discussion around it.
We do this so that you don't waste your time with a change that we have no plans of accepting.
For smaller changes that will take less than an hour or so to work on, its probably best to bypass the issue and go straight to submitting a PR.

Snake follows TDD to the point of pragmatism.
New features or bug fixes must be accompanied by tests and all existing tests must pass in CI before merging.
Changes will be merged after getting a thumbs up from an admin.

## Development Setup

To use your dev version of snake, you will first need to install development dependencies and wire up the development version of the script.
From inside the top level snake development directory, run

```
alias snakedev="PYTHONPATH=`pwd` `pwd`/bin/snake"
snakedev bootstrap install
```

You could instead alias to `snake`, but remember to `unalias` when you are done developing in order to switch back to the installed version.

Another option would be to run the following whenever you make changes.

```
python setup.py install
```

This will install the `snake` binary to your python distribution and put it on your path.
The downside to this is that its easy to forget to do this each time.

### Running Tests

While developing, you can either run tests for the current environment using `nosetests` or you can run tests against all supported Python versions using `tox`.
A good workflow would be to use `nosetests` until you are ready to commit changes and then use `tox` to make sure those changes are compatible with other versions.
