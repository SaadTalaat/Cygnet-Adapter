#!/bin/bash
set -e
set -x
set -o pipefail
export PYENV_ROOT="$PWD/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if [[ "$(uname -s)" == "Darwin" ]]; then
eval "$(pyenv init -)"
else
if [[ "${TOX_ENV}" == "pypy" ]]; then
eval "$(pyenv init -)"
pyenv global pypy-2.6.0
fi
fi
source ~/.venv/bin/activate
tox -v
