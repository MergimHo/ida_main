<!-- omit in toc -->
# IDA recruitment test

IDA (**I**n**D**ex re**A**der) is an API for providing data from the well-known share indices ([DAX](https://en.wikipedia.org/wiki/DAX) & [S&P](https://en.wikipedia.org/wiki/S%26P_Global_Ratings)). It is intended to represent an exemplary application that exists within [Union Investment](https://www.union-investment.de/startseite) and is designed to test the basic programming skills of applicants.

Technically, [Python 3](https://www.python.org/) and [FastAPI](https://fastapi.tiangolo.com/) are used for the API. Both technologies allow fast and stable web service development.

<!-- omit in toc -->
## Table of Contents

- [Preparation](#preparation)
- [Exercises](#exercises)
	- [Excercise 1](#excercise-1)
	- [Excercise 2](#excercise-2)
	- [Excercise 3](#excercise-3)

## Preparation

Before you start, you must:

- Install [Python 3.10.x.](https://www.python.org/downloads/)
- Install [Pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

To activate this project's virtualenv, run following command:

```python
pipenv shell
```

Then install the whole project dependencies with:

```python
pipenv install --dev
```

After successful installation the API can be started locally with the command:

```python
uvicorn main:app --reload
```

You will now be able of accessing the API via your browser on [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Exercises

Please complete the exercises within one week and submit the results as previously agreed.We will discuss the task together in a subsequent interview. All tasks can be solved with the help of the [documentation](https://fastapi.tiangolo.com/).

If you have direct questions about the Recrutiment Test, you can contact us directly via e-mail at [cloudoperations@union-investment.de](mailto:cloudoperations@union-investment.de).

**Good luck with the exercises!**

### Excercise 1

Extend the API with another endpoint that should be accessible via the `/getdata` path. This endpoint is to return all share indices in a list page by page. Each page should contain a maximum of 30 elements.

### Excercise 2

Please complete the `create_upload_files` method so that you can update share indices data at runtime. The data should be sent in the form of a CSV file using an HTTP POST request.

For example, the following curl command can be used for testing:

```bash
curl -d @daxsp.csv http://127.0.0.1:8000/uploadfile
```
or for windows:
```cmd
curl -X POST -F "file=@daxsp.csv"  http://127.0.0.1:8000/uploadfile/
````

[Note in the documentation](https://fastapi.tiangolo.com/tutorial/request-files/)

### Excercise 3

Finally, please write appropriate unit tests for your two tasks using the [components provided by FastAPI](https://fastapi.tiangolo.com/tutorial/testing/).
To do this, expand the test_main.py file. The tests can be run with the following command:

```python
pytest
```

---
***Copyright © 2023 Union IT-Services GmbH. All rights reserved.***
