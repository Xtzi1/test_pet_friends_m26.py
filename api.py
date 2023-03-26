
import json
from settings import valid_email, valid_password
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import logging
import functools


def log_api(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if isinstance(response, tuple):
            status, result = response
        else:
            status, result = response.status_code, response.text

        with open('log.txt', 'a') as f:
            f.write(f'\n--- Request ---\n')
            if hasattr(response, 'request'):
                f.write(f'Method: {response.request.method}\n')
            f.write(f'Status: {status}\n')
            f.write(f'Response: {result}\n')
        return response
    return wrapper



class PetFriends:
    """апи библиотека к веб приложению Pet Friends"""

    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    @log_api
    def get_api_key(self, email: str, passwd: str) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с уникальным ключем пользователя, найденного по указанным email и паролем"""

        headers = {
            'email': email,
            'password': passwd,
        }
        res = requests.get(self.base_url+'api/key', headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @log_api
    def get_list_of_pets(self, auth_key: json, filter: str = "") -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате JSON
        со списком наденных питомцев, совпадающих с фильтром. На данный момент фильтр может иметь
        либо пустое значение - получить список всех питомцев, либо 'my_pets' - получить список
        собственных питомцев"""

        headers = {'auth_key': auth_key['key']}
        filter = {'filter': filter}

        res = requests.get(self.base_url + 'api/pets', headers=headers, params=filter)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @log_api
    def add_new_pet(self, auth_key: json, name: str, animal_type: str, age: str,
                    pet_photo: str) -> json:
        """Метод постит информацию о новом питомце на сервере,
        возвращает статус запроса и JSON с данными питомца"""
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age,
        }
        headers = {'auth_key': auth_key['key']}
        file = {'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')}

        res = requests.post(self.base_url + 'api/pets', headers=headers, data=data, files=file)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @log_api
    def delete_pet(self, auth_key: json, pet_id: str) -> json:
        """Метод удаляет питомца по ID и возвращает статус запроса
        и результат в формате JSON с текстом уведомления о успешном удалении"""
        headers = {'auth_key': auth_key['key']}

        res = requests.delete(self.base_url + f'api/pets/{pet_id}', headers=headers)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @log_api
    def update_pet_info(self, auth_key: json, pet_id: str, name: str, animal_type: str, age: str):
        """Метод обновляет информацию о питомце по его ID и возвращает статус запроса
        и результат в формате JSON с обновленными данными питомца"""
        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }

        res = requests.put(self.base_url + f'api/pets/{pet_id}', headers=headers, data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @log_api
    def add_new_pet_without_photo(self, auth_key: json, name: str,
                                  animal_type: str, age: str) -> json:
        """Метод добавляет нового пета без изображения, на выходе - статус запроса
        и json с данными нового питомца"""
        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }

        res = requests.post(self.base_url + 'api/create_pet_simple', headers=headers, data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    @log_api
    def add_pet_photo(self, auth_key: json, pet_id: str, pet_photo: str):
        """Метод добавляет фото к существующему пету без фото возвращает статус запроса
        и результат в формате JSON"""
        headers = {'auth_key': auth_key['key']}
        file = {'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')}

        res = requests.post(self.base_url + f'api/pets/set_photo/{pet_id}',
                            headers=headers, files=file)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result


