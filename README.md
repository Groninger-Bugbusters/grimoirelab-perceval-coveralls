# perceval-coveralls [![Build Status](https://github.com/Groninger-Bugbusters/grimoirelab-perceval-coveralls/workflows/build/badge.svg)](https://github.com/Groninger-Bugbusters/grimoirelab-perceval-coveralls/actions?query=workflow:build+branch:master+event:push) [![Coverage Status](https://img.shields.io/coveralls/Groninger-Bugbusters/grimoirelab-perceval-coveralls.svg)](https://coveralls.io/r/Groninger-Bugbusters/grimoirelab-perceval-coveralls?branch=master)

Bundle of Perceval backends for Coveralls.

## Backends

The backends currently managed by this package support the next repositories:

* Coveralls

## Requirements

* Python >= 3.6
* python3-requests >= 2.7
* grimoirelab-toolkit >= 0.1.12
* perceval >= 0.17.1

## Installation

To install this package you will need to clone the repository first:

```
$ git clone https://github.com/Groninger-Bugbusters/grimoirelab-perceval-coveralls.git
```

Then you can execute the following commands:
```
$ pip3 install -r requirements.txt
$ pip3 install -e .
```

In case you are a developer, you should execute the following commands to install Perceval in your working directory (option `-e`) and the packages of requirements_tests.txt.
```
$ pip3 install -r requirements.txt
$ pip3 install -r requirements_test.txt
$ pip3 install -e .
```

## Examples

### Running coveralls for a specific repository
```
$ perceval coveralls github chaoss/grimoirelab-perceval
```

### Arguments
The first argument should be the service used, either github, gitlab, or bitbucket.

The second argument should be the repository name as it appears in the coveralls url:
for https://coveralls.io/github/chaoss/grimoirelab-perceval, the argument would be chaoss/grimoirelab-perceval


## License

Licensed under GNU General Public License (GPL), version 3 or later.
