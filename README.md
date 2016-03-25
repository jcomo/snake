# snake

Build script utility for Python. Ported from the popular Ruby tool, [Rake](https://github.com/ruby/rake).

## Development Setup

To use your dev version of snake, you will need to wire it up first. From inside the top level snake development directory, run

```
alias snake="PYTHONPATH=`pwd` `pwd`/bin/snake"
```

Now you will be running the dev version of snake. To revert to your installed copy, simply use

```
unalias snake
```
