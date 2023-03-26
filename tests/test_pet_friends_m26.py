from api import PetFriends, log_api
from settings import valid_email, valid_password
import os
import pytest

pf = PetFriends()


class TestPetFriends:
    @pytest.fixture(autouse=True)
    def api_client(self):
        #setup
        self.pf = PetFriends()
        status, self.auth_key = self.pf.get_api_key(valid_email, valid_password)
        assert status == 200
        yield

    @pytest.fixture()
    def clean_data(self):
        #teardown
        self.pf.delete_pet(self.auth_key)


    @pytest.mark.auth
    @pytest.mark.api
    def test_get_api_key_for_valid_user(self, email=valid_email, password=valid_password):
        """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
        status, result = pf.get_api_key(email, password)

        # Сверяем полученные данные с нашими ожиданиями
        assert status == 200
        assert 'key' in result


    @pytest.mark.api
    def test_get_all_pets_with_valid_key(self, filter=''):
        """ Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо '' """

        status, result = self.pf.get_list_of_pets(self.auth_key, filter)

        assert status == 200
        assert len(result['pets']) > 0


    @pytest.mark.api
    @pytest.mark.manipulations_with_pets
    def test_add_new_pet_with_valid_data(self, name='Барбоскин', animal_type='двортерьер',
                                         age='47', pet_photo='images/cat1.jpg'):
        """Проверяем что можно добавить питомца с корректными данными"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Добавляем питомца
        status, result = self.pf.add_new_pet(self.auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    @pytest.mark.api
    def test_successful_delete_self_pet(self):
        """Проверяем возможность удаления питомца"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        # _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        # Проверяем - если список своих питомцев пустой, то добавляем нового
        # и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            pf.add_new_pet(self.auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
            _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id']
        status, _ = pf.delete_pet(self.auth_key, pet_id)

        # Ещё раз запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
        assert status == 200
        assert pet_id not in my_pets.values()

    @pytest.mark.api
    def test_successful_update_self_pet_info(self, name='Мурзик', animal_type='Котэ', age=5):
        """Проверяем возможность обновления информации о питомце"""

        # Получаем ключ auth_key и список своих питомцев
        # _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        # Если список не пустой, то пробуем обновить его имя, тип и возраст
        if len(my_pets['pets']) > 0:
            status, result = pf.update_pet_info(self.auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

            # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
            assert status == 200
            assert result['name'] == name
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")


#################################################################
#################################################################
#                 ДАЛЕЕ МОИ ТЕСТЫ
#################################################################
#################################################################

    @pytest.mark.api
    @pytest.mark.manipulations_with_pets
    def test_add_new_pet_without_photo(self, name='Томми the Cat', animal_type='kit', age='3'):
        """Проверяем что можно добавить пета без фото"""

        # Получаем ключ auth_key и сохраняем в переменную
        # _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet_without_photo(self.auth_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    @pytest.mark.api
    def test_add_pet_photo(self, pet_photo="images/cat1.jpg"):
        """Проверяем что можно добавить пету фото"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем ключ auth_key и сохраняем в переменную
        # _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(self.auth_key, 'my_pets')

        # Если не пустой, то пробуем запостить фото
        if len(my_pets['pets']) > 0:
            status, result = pf.add_pet_photo(self.auth_key, my_pets['pets'][0]['id'], pet_photo)

            # Проверяем что статус ответа = 200
            assert status == 200
        else:
            # если спиок питомцев пустой, то выкидываем исключение
            # с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")

    @pytest.mark.api
    def test_add_new_pet_with_invalid_auth_key(self, name='Жерар', animal_type='Sobaken', age='5', pet_photo='images/cat1.jpg'):
        """Проверяем что нельзя добавить пета с невалидным api ключом"""
        auth_key = {'key': 'qwe83'}
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 403

    @pytest.mark.api
    @pytest.mark.auth
    def test_unsuccessful_get_auth_key_with_invalid_email(self, email='s0d@s0od.er', password=valid_password):
        """ Проверяем что запрос api ключа возвращает статус 403 если ввести невалидный эмейл"""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
        status, _ = pf.get_api_key(email, password)

        # Сверяем полученные данные с нашими ожиданиями
        assert status == 403

    @pytest.mark.api
    @pytest.mark.auth
    def test_unsuccessful_get_auth_key_with_invalid_password(self, email=valid_email, password='qweoi3'):
        """ Проверяем что запрос api ключа возвращает статус 403 если ввести невалидный пароль"""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
        status, _ = pf.get_api_key(email, password)

        # Сверяем полученные данные с нашими ожиданиями
        assert status == 403

    @pytest.mark.api
    @pytest.mark.manipulations_with_pets
    def test_add_new_pet_with_png_photo(self, name='Барбоскин', animal_type='двортерьер',
                                         age='4', pet_photo='images/00013.png'):
        """Проверяем что можно добавить питомца с корректными данными и фото в формате png"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        # _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet(self.auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    @pytest.mark.skip
    @pytest.mark.xfail
    @pytest.mark.api
    def test_unsuccessful_add_new_pet_with_empty_values(self, name='', animal_type='',
                                         age='', pet_photo='images/00013.png'):
        """Проверяем что если отправить пустые значения при создании пета, то сервер вернет ошибку
        И ВИДИМ ЧТО ЗДЕСЬ БАГ, так как сервер возвращает 200"""

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        # _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet(self.auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 400
        assert result['name'] != name

    @pytest.mark.api
    @pytest.mark.manipulations_with_pets
    def test_add_new_pet_with_huge_values(self,
            name='БарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскинБарбоскин',
            animal_type='двортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьердвортерьер',
            age='999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999',
            pet_photo='images/00013.png'):
        """Проверяем что можно добавить питомца с слишком большими данными"""

        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        # _, auth_key = pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = pf.add_new_pet(self.auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    @pytest.mark.xfail
    @pytest.mark.api
    @pytest.mark.skip
    def test_unsuccessful_update_pet_info_with_empty_values(self, name='', animal_type='', age=''):
        """Проверяем невозможность обновления информации о питомце пустыми полями
        И НАХОДИМ БАГ, потому что при отправке пустых полей с сервера приходит 200"""

        # Получаем ключ auth_key и список своих питомцев
        # _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        # Если список не пустой, то пробуем обновить его имя, тип и возраст
        if len(my_pets['pets']) > 0:
            status, result = pf.update_pet_info(self.auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

            # Проверяем что статус ответа = 400 и имя питомца отсутствует в списке
            assert status == 400
            assert result['name'] == name
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")
    @pytest.mark.api
    def test_delete_pet_with_wrong_auth_key(self):
        """Проверяем удаление питомцев с невалидным ключом апи"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        # _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        # Проверяем - если список своих питомцев пустой, то добавляем нового
        # и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            pf.add_new_pet(self.auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
            _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id']
        auth_key = {'key': 'qwe83'}
        status, _ = pf.delete_pet(auth_key, pet_id)

        # # Ещё раз запрашиваем список своих питомцев
        # _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем что статус ответа равен 403 и в списке питомцев нет id удалённого питомца
        assert status == 403
        assert pet_id not in my_pets.values()