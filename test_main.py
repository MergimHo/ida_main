import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import random

from main import app, get_fake_items_db


# GLOBAL SETUP VARIABLES
START_DATE = '01.01.2018'

SIMPLE_TEST_DATA = {
        '20150501': {'DAX': '1', 'SP500': '600'},
        '20150502': {'DAX': '2', 'SP500': '1200'},
        }

# GLOBAL TEST SETUP

@pytest.fixture
def client():
    return TestClient(app)


# First example test.
def test_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.text.find("Swagger") != -1
    assert 1 == 1


"""
TESTS FOR EXERCISE 1
"""

# test helper function, bc its essential that it works and it contains some complexity.
def test_helper_function():
    # 60 days from 01.01.2018 is the 01.03.2018
    number_of_expected_entries = 60
    data = generate_test_data(number_of_expected_entries, START_DATE)
    assert data.get('20180301') is not None
    assert data.get('20180302') is None


# /getDataAll with invalid index (not 'DAX' or 'SP500') should return HTTPException
def test_invalid_index_for_getAll(client):
    ERROR_MSG = "Invalid Index parameter. Please choose 'DAX', 'SP500' or 'ALL'."
    exception_response = client.get("/getdata?index=INVALID_INDEX")
    assert exception_response.status_code == 400
    assert exception_response.json()["detail"] == ERROR_MSG


# /getDataAll with null should return 200 and the 'ALL' information in its header.
def test_null_index_for_getAll_should_return_all(client):
    exception_response = client.get("/getdata")
    assert exception_response.status_code == 200
    assert exception_response.headers["requested-index"] == "ALL"


# /getDataAll should return just the index of 'DAX' explicit
def test_values_match_dax_explicit(client, mocker):
    dax_values = ['1', '2']
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    dax_reponse = client.get("/getdata?index=DAX")
    body = dax_reponse.json()
    body_values = [indice[1] for page in body for indices in page.values() for indice in indices]
    assert body_values == dax_values


# /getDataAll should return just the index of 'DAX'
def test_index_DAX_should_not_contain_SP500(client, mocker):
    data = generate_test_data(number_of_entries=20, start_date=START_DATE)
    mocker.patch('main.fake_items_db', data)

    dax_reponse = client.get("/getdata?index=DAX")
    body = dax_reponse.json()

    dax_values = [value['DAX'] for value in data.values()]
    body_values = [indice[1] for page in body for indices in page.values() for indice in indices]
    assert body_values == dax_values


# /getDataAll should return just the index of 'DAX' explicit
def test_values_match_sp500_explicit(client, mocker):
    sp500_values = ['600', '1200']
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    sp500_response = client.get("/getdata?index=SP500")
    body = sp500_response.json()
    body_values = [indice[1] for page in body for indices in page.values() for indice in indices]
    assert body_values == sp500_values


# /getDataAll should reuturn just the index of 'SP500'
def test_index_SP500_should_not_contain_DAX(client, mocker):
    data = generate_test_data(number_of_entries=20, start_date=START_DATE)
    mocker.patch('main.fake_items_db', data)

    dax_reponse = client.get("/getdata?index=SP500")
    body = dax_reponse.json()

    sp500_values = [value['SP500'] for value in data.values()]
    body_values = [indice[1] for page in body for indices in page.values() for indice in indices]
    assert body_values == sp500_values


"""
Here we craete a fake_db with a certain amount of entries and the expected pages.
We test /getdata and /getdatAll here together because focus in this test on page numbers.
"""
@pytest.mark.parametrize("num_of_entries, expected_pages", [
    (0, 0), (29, 1), (30, 1), (31, 2), (60, 2),
    (61, 3), (88, 3), (89, 3), (90, 3), (91, 4),
    (1412, 48)
])
def test_correct_page_numbers_by_index(client, mocker, num_of_entries, expected_pages):
    data = generate_test_data(number_of_entries=num_of_entries, start_date=START_DATE)
    mocker.patch('main.fake_items_db', data)

    response_by_index = client.get("/getdata?index=DAX")

    assert response_by_index.status_code == 200, "Status code was not 200 as expected"
    assert len(response_by_index.json()) == expected_pages, f"Page number was {len(response_by_index.json())} not as expected {expected_pages}"

    response_all = client.get("/getdataAll")

    assert response_all.status_code == 200, "Status code was not 200 as expected"
    assert len(response_all.json()) == expected_pages, f"Page number was {len(response_all.json())} not as expected {expected_pages}"


"""
TESTS FOR EXERCISE 2
"""
# POST of csv that is NULL
def test_csv_is_null(client, mocker):
    ERROR_MSG =  "No file uploaded."
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    empty_bytes = b''

    post_request = client.post('/uploadfile/', files={"file": (f"daxsp_c.csv", empty_bytes)})
    assert post_request.status_code == 400
    assert post_request.json()["detail"] == ERROR_MSG



# POST if does not end with *.csv
def test_csv_ends_not_with_csv(client, mocker):
    FILE_ENDING = 'XXX'
    ERROR_MSG =  "Only CSV data allowed. File ending must be *.csv or correct content-type."
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    with open("test_resources\daxsp_c.csv", "rb") as csv_file:
        file_bytes = csv_file.read()

    post_request = client.post('/uploadfile/', files={"file": (f"daxsp_c.{FILE_ENDING}", file_bytes)})
    assert post_request.status_code == 415
    assert post_request.json()["detail"] == ERROR_MSG


# POST if content_type is  ['application/vnd.ms-excel', 'text/csv']
def test_csv_correct_content_type(client, mocker):
    ALLOWED_CONTENT_TYPE =  ['application/vnd.ms-excel', 'text/csv']
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    with open("test_resources\daxsp_c.csv", "rb") as csv_file:
        file_bytes = csv_file.read()

    for content_type in ALLOWED_CONTENT_TYPE:
        post_request = client.post('/uploadfile/', files={"file": (f"daxsp_c.csv", file_bytes, content_type)})
        assert post_request.status_code == 201


# POST if content_type is not  ['application/vnd.ms-excel', 'text/csv']
def test_csv_wrong_content_type(client, mocker):
    WRONG_CONTENT_TYPE = "application/json"
    ERROR_MSG =  "Only CSV data allowed. File ending must be *.csv or correct content-type."
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    with open("test_resources\daxsp_c.csv", "rb") as csv_file:
        file_bytes = csv_file.read()

    post_request = client.post('/uploadfile/', files={"file": (f"daxsp_c.csv", file_bytes, WRONG_CONTENT_TYPE)})
    assert post_request.status_code == 415
    assert post_request.json()["detail"] == ERROR_MSG


# Check that entries were added. in SIMPLE_TEST_DATA we have 2 entries, we add 3 more. 
def test_upload_csv_contains_3_entries(client, mocker):
    EXPECTED_ENTRIES = 5
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    with open("test_resources\daxsp_c.csv", "rb") as csv_file:
        file_bytes = csv_file.read()

    post_request = client.post('/uploadfile/', files={"file": ("daxsp_c.csv", file_bytes)})
    db = get_fake_items_db()
    
    assert post_request.status_code == 201
    assert len(db) == EXPECTED_ENTRIES



# Check that entries are sorted 
def test_final_db_is_sorted(client, mocker):
    mocker.patch('main.fake_items_db', SIMPLE_TEST_DATA)

    with open("test_resources\daxsp_c.csv", "rb") as csv_file:
        file_bytes = csv_file.read()

    post_request = client.post('/uploadfile/', files={"file": ("daxsp_c.csv", file_bytes)})
    dates_from_db = list(get_fake_items_db().keys())
    formatted_dates_from_db = [datetime.strptime(date, "%Y%m%d") for date in dates_from_db]

    assert all(formatted_dates_from_db[i] >= formatted_dates_from_db[i+1] for i in range(len(formatted_dates_from_db)-1))




# HELPER FUNCTIONS

"""
This function will generate a dict that contains data in the format 
{<DATE> : {'DAX' : <NUMBER> : 'SP500': <NUMBER>}} by the entries and a start date.
The start date will increase by a day.
Note that for readability we entered START_DATE as %d.%m.%Y.
"""
def generate_test_data(number_of_entries: int, start_date: str):
    data = {}
    current_date = datetime.strptime(start_date, '%d.%m.%Y')
    for i in range(number_of_entries):
        data[current_date.strftime('%Y%m%d')] = {
            'DAX' : str(random.randint(1,1000)),
            'SP500' : str(random.randint(1,1000))
        }
        current_date += timedelta(days=1)
    
    return data




