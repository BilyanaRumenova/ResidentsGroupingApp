import io

from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["Content-Type"]


def test_handle_data_with_csv_file():
    csv_data = ("Name,Address\nIvan Ivanov, 'ul. Testova 10, Sofia, Bulgaria'\n"
                "Georgi Petrov, 'Testova 10, Sofia, Bulgaria'\nMaria Ivanova, 'Berlin, Germany'")
    files = {"csv_file": ("test.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    response = client.post("/process-data", files=files)
    assert response.status_code == 200
    assert "processed_data" in response.json()
    expected_data = {
        "processed_data": "Georgi Petrov, Ivan Ivanov\n"
                          "Maria Ivanova"
    }
    assert response.json() == expected_data


def test_handle_data_with_valid_text_input():
    data = ("Ivan Ivanov, 'ul. Test 10, Sofia, Bulgaria'\nGeorgi Petrov,"
            " 'Test Street 10, Sofia, Bulgaria'\nMaria Ivanova, 'Berlin, Germany'")
    response = client.post("/process-data", data={"text_input": data})
    assert response.status_code == status.HTTP_200_OK
    assert "processed_data" in response.json()
    expected_data = {
        "processed_data": "Georgi Petrov, Ivan Ivanov\n"
                          "Maria Ivanova"
    }
    assert response.json() == expected_data

def test_handle_data_with_cyrillic_symbols():
    data = ("Ivan Ivanov, 'София, България'\nGeorgi Petrov, "
            "'Sofia, Bulgaria'\nMaria Ivanova, 'Berlin, Germany'\nIvan Georgiev, 'Берлин, Германия'")
    response = client.post("/process-data", data={"text_input": data})
    assert response.status_code == status.HTTP_200_OK
    assert "processed_data" in response.json()
    expected_data = {
        "processed_data": "Georgi Petrov, Ivan Ivanov\n"
                          "Ivan Georgiev, Maria Ivanova"
    }
    assert response.json() == expected_data


def test_handle_data_with_invalid_text_input():
    data = "some random text"
    response = client.post("/process-data", data={"text_input": data})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Error processing data'}
