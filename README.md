### yoyocoin
PoS crypto coin over ipfs distributed storage network (with new consensus protocol 🙌)

[![Full tests](https://github.com/yoyocoin/yoyocoin/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/yoyocoin/yoyocoin/actions/workflows/tests.yml)
[![Bring Them Home](https://badge.yehoyada.com)](https://www.standwithus.com/)  

#### WORK IN PROGRESS
this project is a work in progress and dose not ready for production
#### Developer section
##### install dev requirements
```shell script
pip install -r requirements-dev.txt
```

##### run tests
```shell script
pytest
mypy src
flake8 src --max-line-length=127
```

##### test multiple python versions with tox
```shell script
tox -c tox.ini
```

##### check coverage
```shell script
coverage run -m pytest
coverage html
```
