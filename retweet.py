import time, datetime, re, json, selenium.common.exceptions, warnings, random
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ActionChains

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Преобразует обычный текст от пользователя в удобный Json формат для дальнейшей работы.
def txt_to_json():
    with open('text_list.txt', 'r') as f:
        text_list_text = f.read().splitlines()

    with open('twitter_links.txt', 'r') as f:
        twitter_links_text = f.read().splitlines()

        links_text_dict = {}
        for links_text in twitter_links_text:
            links_text_dict[links_text] = 0

    with open('opensea_twitter_list.txt', 'r') as f:
        opensea_twitter_list = f.read().splitlines()

        twitter_list_dict = {}
        for links_text in opensea_twitter_list:
            twitter_list_dict[links_text] = 0

    list_dict_to_json = {}
    list_dict_to_json['text_list'] = text_list_text
    list_dict_to_json['twitter_links'] = links_text_dict
    list_dict_to_json['opensea_twitter'] = twitter_list_dict

    with open('./tools/jsont_from_text.json', 'w', encoding='utf-8') as file:
        json.dump(list_dict_to_json, file, indent=4, ensure_ascii=False)


# Читает списки ссылок
def json_links_reader():
    with open('./tools/jsont_from_text.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        config_params = {
            'text_list': data['text_list'],
            'twitter_links': data['twitter_links'],
            'opensea_twitter': data['opensea_twitter']
        }
    return config_params


# Читает настройкипарсера
def json_config_reader():
    with open('./config.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        json_config = {
            'account_limit': data['account_limit'],
            'twitter_links_limit': data['twitter_links_limit']
        }
    return json_config


# Считывает данные аккаунтов для последующего ввода в парсере
def json_accounts_date():
    with open('./tools/user_date.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return len(data), data


def load_json_twitter_links():
    load_config_links_limit = json_config_reader()

    with open('./tools/jsont_from_text.json', 'r', encoding='utf-8') as json_file:
        old_data_dict = json.load(json_file)
        for link in old_data_dict['twitter_links']:
            if old_data_dict['twitter_links'][link] < load_config_links_limit['twitter_links_limit']:
                return link
            else:
                pass
        return 'twitter_links_end'


# Записывает количество использований аккаунта
def update_user_count_and_date(user):
    load_config_acc = json_config_reader()

    try:
        with open('./tools/user_date.json', 'r', encoding='utf-8') as json_file:
            old_data_dict = json.load(json_file)
    except json.decoder.JSONDecodeError:
        old_data_dict = {}
        pass

    if int(old_data_dict[f'{user}']['number_of_subscriptions']) >= int(load_config_acc['account_limit']):
        pass
    else:
        old_data_dict[f'{user}']['number_of_subscriptions'] = old_data_dict[f'{user}']['number_of_subscriptions'] + 1

        now = datetime.datetime.now()
        old_data_dict[f'{user}']['last_date_use'] = now.strftime("%d-%m-%Y %H:%M")

        try:
            file_json = open('./tools/user_date.json', 'w+', encoding='utf-8')
            json.dump(old_data_dict, file_json, indent=4, ensure_ascii=False)
            file_json.close()

            return
        except PermissionError:
            print('Нет доступа к файлу config.json')

# Записывает количество упоминаний одной ссылки
def update_json_general_twitter_link(url_general_twitter_link):
    with open('./tools/jsont_from_text.json', 'r', encoding='utf-8') as json_file:
        old_data_dict = json.load(json_file)
        old_data_dict['twitter_links'][url_general_twitter_link] = old_data_dict['twitter_links'][
                                                                       url_general_twitter_link] + 1

    try:
        file_json = open('./tools/jsont_from_text.json', 'w+', encoding='utf-8')
        json.dump(old_data_dict, file_json, indent=4, ensure_ascii=False)
        file_json.close()
    except PermissionError:
        print('Нет доступа к файлу jsont_from_text.json')

# Записывает применение кнопки "Follow", у пользователя.
def update_json_url_user_twitter(url_user_twitter):
    with open('./tools/jsont_from_text.json', 'r', encoding='utf-8') as json_file:
        old_data_dict = json.load(json_file)
        old_data_dict['opensea_twitter'][url_user_twitter] = old_data_dict['opensea_twitter'][url_user_twitter] + 1

    try:
        file_json = open('./tools/jsont_from_text.json', 'w+', encoding='utf-8')
        json.dump(old_data_dict, file_json, indent=4, ensure_ascii=False)
        file_json.close()
    except PermissionError:
        print('Нет доступа к файлу jsont_from_text.json')


# Получает все аккаунты из json файла.
def account_date_loader():
    load_config_acc = json_config_reader()
    date_user = {}
    for acc_id in range(1, json_accounts_date()[0] + 1):
        # Проверяет, есть лимит на аккаунте или нет.
        if int(json_accounts_date()[1][f'user_{acc_id}']['number_of_subscriptions']) < int(
                load_config_acc['account_limit']) and json_accounts_date()[1][f'user_{acc_id}']['status_off'] == 1:

            date_user['acc_id'] = f'user_{acc_id}'
            date_user['phone_number'] = json_accounts_date()[1][f'user_{acc_id}']['phone_number']
            date_user['password'] = json_accounts_date()[1][f'user_{acc_id}']['password']
            date_user['security_nick'] = json_accounts_date()[1][f'user_{acc_id}']['security_nick']
            date_user['security_email'] = json_accounts_date()[1][f'user_{acc_id}']['security_email']
            date_user['number_of_subscriptions'] = json_accounts_date()[1][f'user_{acc_id}']['number_of_subscriptions']

            return date_user  # Возврат данных учетной записи для работы парсера

        else:
            print(f'На аккаунте {json_accounts_date()[1][f"user_{acc_id}"]["phone_number"]} превышен лимит - '
                  f'{json_accounts_date()[1][f"user_{acc_id}"]["number_of_subscriptions"]}, пропускаю.')
            print('Или аккаунт выключен status_off - 0')

    print('Нет доступных аккаунтов для выполнения работы \n Закрываю парсер!')
    input('Нажмите любую кнопку для выхода')
    exit()


# Основной парсер, который делает работу
def twitter_sender():
    if load_json_twitter_links() == 'twitter_links_end':
        print('Лимиты всех упоминаний Твитов из главной учетной, исчерпаны!')
        print('Добавьте новые ссылки!')
    else:
        load_user_account = account_date_loader()
        fireFoxOptions = Options()
        fireFoxOptions.add_argument("--headless")
        fireFoxOptions.add_argument('--disable-gpu')
        fireFoxOptions.add_argument('--no-sandbox')
        driver = webdriver.Firefox(options=fireFoxOptions, executable_path=r'./tools/driver/geckodriver.exe')
        driver.implicitly_wait(
            10)  # Неявное ожидание загрузки элемента. Указано максимальное значение, сколько будет ждать

        print('Параметры успешно загружены. Открываю сайт')
        try:
            driver.get('https://twitter.com/')
            driver.refresh()
        except selenium.common.exceptions.WebDriverException:
            print('Ошибка загрузки сайта.')
            input('Нажмите кнопку для выхода')
            driver.close()
            exit()

        try:
            # БЛОК АВТОРИЗАЦИИ НАЧАЛО
            print('Сайт успешно загружен')
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:

                print('Пытаюсь найти кнопку Войти')
                driver.find_element(By.XPATH, "//span[contains(text(),'Войти')]").click()
                print('Нажал кнопку Войти')

            except selenium.common.exceptions.NoSuchElementException:
                print('Другая форма входа')
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print('Пытаюсь найти кнопку Войдите')
                driver.find_element(By.XPATH,
                                    "//span[contains(text(),'Войдите')] | //span[contains(text(),'Используйте номер телефона')]").click()
                print('Нажал кнопку Войдите')

            try:
                driver.refresh()
                print('Пытаюсь ввести номер телефона')
                phone_input = '//*[@autocomplete="username"]'
                driver.find_element(By.XPATH, phone_input).click()
                driver.find_element(By.XPATH, phone_input).send_keys(load_user_account['phone_number'])
                print('Успешно ввел номер телефона')
            except selenium.common.exceptions.NoSuchElementException:
                print('Возникла ошибка на форме ввода логина \n Закрываю парсер!')
                driver.close()
                input('Нажмите любую кнопку для выхода')
                exit()

            print('Нажимаю кнопку Далее')
            driver.find_element(By.XPATH, '//span[contains(text(),"Далее")]').click()

            print('Пытаюсь ввести пароль')
            driver.find_element(By.XPATH, '//*[@autocomplete="current-password"]').send_keys(
                load_user_account['password'])
            print('Успешно ввел пароль')

            print('Пытаюсь нажать кнопку входа')
            driver.find_element(By.XPATH, '//span[contains(text(),"Войти")]').click()
            print('Успешно нажал кнопку входа')

            # Проверка имени пользователя
            try:
                print('Есть проверка дополнительная проверка?')
                text_security = driver.find_element(By.XPATH, '//div[@class="css-1dbjc4n r-knv0ih"]').text

                if 'электронной' in text_security:
                    print('Проверка по почте')
                    driver.find_element(By.XPATH, '//*[@autocapitalize="none"]').send_keys(
                        load_user_account['security_email'])
                    driver.find_element(By.XPATH, '//span[contains(text(),"Далее")]').click()
                    print('Успешно ввел ПОЧТУ пользователя для проверки входа в аккаунт')

                elif 'учетной записью' in text_security:
                    print('Проверка ник')
                    driver.find_element(By.XPATH, '//*[@autocapitalize="none"]').send_keys(
                        load_user_account['security_nick'])
                    driver.find_element(By.XPATH, '//span[contains(text(),"Далее")]').click()
                    print('Успешно ввел Ник пользователя для проверки входа в аккаунт')
                else:
                    print('Возникла безопасности, которой нет в парсере. \n Закрываю парсер!')
                    driver.close()
                    input('Нажмите любую кнопку для выхода')
                    exit()

            except selenium.common.exceptions.NoSuchElementException:
                print('Дополнительная проверка отсутствует')


        except selenium.common.exceptions.NoSuchElementException:
            print('Возникли проблемы с авторизацией')
            print('Закрываю парсер!')
            driver.close()
            exit()

        print('Успешно прошел авторизацию в аккаунте')
        # БЛОК АВТОРИЗАЦИИ КОНЕЦ
        time.sleep(10)

        for url_twitter in json_links_reader()['opensea_twitter']:

            if json_links_reader()['opensea_twitter'][url_twitter] <= 0:
                print(f'Работаю со аккаунтом {url_twitter}')
                next_twitter = url_twitter
                print(f'Открываю {next_twitter}')

                driver.get(next_twitter)  # Переходит по ссылке
                print('Обновляю страницу')
                driver.refresh()

                # Находит название учетной записи с собачкой (@)
                url_user_twitter = str(driver.current_url)
                pattern = r'\w+$'
                find_username_twitter = '@' + str(re.search(pattern, url_user_twitter).group())

                try:
                    # Находит текст в Follow
                    print(f'Пробую нажать кнопку Follow')
                    find_follow_button = driver.find_element(By.XPATH,
                                                             '//span[contains(text(),"Follow" )] | //span[contains(text(),"Читать" )]')

                    print(f'На кнопке {find_follow_button.text}')

                    if find_follow_button.text == 'Follow':
                        print(f'Отсутствует подписка на {find_username_twitter}. \n Нажимаю кнопку Follow')
                        # driver.find_element(By.XPATH,'//span[contains(text(),"Follow" )] | //span[contains(text(),"Читать" )]').click()  # Нажимает кнопку Follow

                        update_user_count_and_date(
                            load_user_account['acc_id'])  # записывает использование кнопки Follow в аккаунте

                        try:
                            if load_json_twitter_links() == 'twitter_links_end':
                                print('Лимиты всех упоминаний Твитов из главной учетной, исчерпаны!')
                                print('Добавьте новые ссылки!')
                                driver.close()
                            else:
                                general_twitter_link = load_json_twitter_links()  # ссылка twitter_links
                                print(f'Возвращаюсь в Твит основной учетной записи - {general_twitter_link}')
                                driver.get(general_twitter_link)

                                # Находит первый твит, жмакает на копку
                                element_image_twit = driver.find_element(By.XPATH, '//img[contains(@alt,"Image")]')
                                driver.execute_script("arguments[0].click();", element_image_twit)
                                print('Нажал на первый твит. \n Ищу кнопку Ретвита')

                                # driver.find_element(By.XPATH, '//div[contains(@aria-label,"Retweets. Retweet")]').click()
                                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, '//div[contains(@aria-label,"Retweets. Retweet")]'))))
                                print('Успешно нажал кнопку Ретвита')

                                print('Нажимаю Quote Tweet')
                                # driver.find_element(By.XPATH, '//span[contains(text(),"Quote Tweet" )]').click()
                                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 50).until(
                                    EC.element_to_be_clickable((By.XPATH, '//a[contains(@href,"/compose/tweet")]'))))
                                print('Успешно нажал Quote Tweet')

                                # Вводит текст в Quote Tweet
                                # print('Пытаюсь ввести текст для Quote Tweet')

                                # # driver.find_element(By.XPATH, '//div[contains(@class,"DraftEditor-root")]').click()
                                # # driver.find_element(By.XPATH, '//div [contains(@class,"public-DraftStyleDefault-block public-DraftStyleDefault-ltr")]').click()

                                text_preparation = find_username_twitter + ' ' + random.choice(
                                    json_links_reader()['text_list'])
                                print(f'Пытаюсь ввести текст Ретвита: {text_preparation}')

                                # Нажимаю в поле ввода
                                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(
                                    EC.element_to_be_clickable((By.XPATH,
                                                                '//div [contains(@class,"public-DraftStyleDefault-block public-DraftStyleDefault-ltr")]'))))
                                # Ввожу текст
                                # driver.find_element(By.XPATH,'//div [contains(@class,"public-DraftStyleDefault-block public-DraftStyleDefault-ltr")]').send_keys(text_preparation)
                                find_text_input = driver.find_element(By.XPATH,
                                                                      '//div [contains(@class,"public-DraftStyleDefault-block public-DraftStyleDefault-ltr")]')
                                ActionChains(driver).move_to_element(find_text_input).click(find_text_input).send_keys(
                                    text_preparation).perform()

                                print('Успешно ввел текст. \n Записываю данные об использовании.')

                                update_json_general_twitter_link(general_twitter_link)  # Записывает упоминания аккаунта
                                update_json_url_user_twitter(url_twitter)  # Записывает количество упоминания твита
                                print('Тут должно быть нажатие на кнопку Tweet, но сейчас пропускаем.')
                                print('Немного жду, прежде чем прейти к другому аккаунту')
                                time.sleep(random.randint(20, 25))

                        except selenium.common.exceptions.NoSuchElementException:
                            # except NotImplemented:
                            print('Ошибка ретвита')


                    elif find_follow_button.text == 'Following':
                        print(f'Уже подписан на этого пользователя {find_username_twitter} \n Пропускаю')

                except selenium.common.exceptions.NoSuchElementException:
                    print('Отсутствует кнопка Follow/Following или возникли проблемы на сайте')

            else:
                print(f'Этот аккаунт уже упоминался ранее {url_twitter}')

        print('Закончились twitter аккаунты opensea или исчерпаны лимиты.')
        driver.close()  # закрыть браузер после всех действий


if __name__ == '__main__':
    print('Запуск скрипта')
    twitter_sender()
    input('Нажмите любую кнопку для выхода')
    exit()
