import os
import uuid

import pytest
import requests

BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = os.getenv('YA_DISK_TOKEN')
AUTH_HEADERS = {'Authorization': f'OAuth {TOKEN}'}

pytestmark = pytest.mark.skipif(not TOKEN, reason='Не задана переменная окружения YA_DISK_TOKEN')


def create_folder(path, headers=AUTH_HEADERS):
    return requests.put(BASE_URL, params={'path': path}, headers=headers, timeout=15)


def get_resource(path, **extra_params):
    return requests.get(BASE_URL, params={'path': path, **extra_params},
                        headers=AUTH_HEADERS, timeout=15)


def delete_folder(path):
    return requests.delete(BASE_URL, params={'path': path, 'permanently': 'true'},
                           headers=AUTH_HEADERS, timeout=15)


@pytest.fixture
def folder_name():
    name = f'autotest_{uuid.uuid4().hex[:8]}'   # уникальное имя, тесты не мешают друг другу
    yield name
    delete_folder(name)                          # уборка выполняется даже если тест упал


# ---------- положительные тесты ----------

def test_create_folder_returns_201(folder_name):
    response = create_folder(folder_name)
    assert response.status_code == 201
    assert 'href' in response.json()


def test_created_folder_appears_in_file_list(folder_name):
    create_folder(folder_name)

    response = get_resource('/', limit=100, sort='-created')   # новые файлы первыми
    assert response.status_code == 200

    items = response.json()['_embedded']['items']
    folder = next((item for item in items if item['name'] == folder_name), None)
    assert folder is not None, 'папка не появилась в списке файлов'
    assert folder['type'] == 'dir'


# ---------- отрицательные тесты ----------

def test_create_existing_folder_returns_409(folder_name):
    create_folder(folder_name)
    response = create_folder(folder_name)       # второй раз ту же папку
    assert response.status_code == 409
    assert response.json()['error'] == 'DiskPathPointsToExistentDirectoryError'


def test_create_folder_in_missing_parent_returns_409(folder_name):
    response = create_folder(f'{folder_name}/child')   # родительской папки нет
    assert response.status_code == 409
    assert response.json()['error'] == 'DiskPathDoesntExistsError'


@pytest.mark.parametrize('headers', [
    {},
    {'Authorization': 'OAuth invalid_token'},
], ids=['no_token', 'wrong_token'])
def test_create_folder_unauthorized_returns_401(folder_name, headers):
    response = create_folder(folder_name, headers=headers)
    assert response.status_code == 401
