import logging
from datetime import datetime
import os
from functools import reduce

import requests

logging.basicConfig(level=logging.INFO)


def get_data(url):
    try:
        data = requests.get(url)
        if data.status_code != 200:
            logging.error(f'Ошибка! {url} Код ответа: {data.status_code}')
            exit(1)
        else:
            logging.info(f'{url} Данные успешно получены.')
    except Exception as e:
        logging.exception(f'Ошибка! {e}')
        exit(1)
    return data.json()


def stringify(user_id, tasks):
    user_tasks = filter(lambda task: task['userId'] == user_id, tasks)

    def helper(acc, task):
        if task['completed']:
            acc[0] += cut(task['title'])
        else:
            acc[1] += cut(task['title'])
        return acc

    return reduce(helper, user_tasks, ['', ''])


def cut(string):
    if len(string) > 50:
        string = f'{string[:50]}...'
    return string + '\n'


def main():
    users = get_data('https://json.medrating.org/users')
    tasks = get_data('https://json.medrating.org/todos')

    if not os.path.exists('tasks'):
        os.mkdir('tasks')

    for user in users:
        date = datetime.now().strftime('%d.%m.%Y %H:%M')
        [complete, incomplete] = stringify(user['id'], tasks)

        text = f'''
{user["name"]} <{user["email"]}> {date}
{user["company"]["name"]}

Завершенные задачи:
{complete.strip()}

Оставшиеся задачи:
{incomplete.strip()}
'''
        filename = f'tasks/{user["username"]}.txt'
        if os.path.exists(filename):
            mod_date = datetime.fromtimestamp(os.path.getmtime(filename)).strftime("%Y-%m-%dT%H:%M")
            os.renames(filename, f'{filename[:-4]}_{mod_date}.txt')
        with open(f'tasks/{user["username"]}.txt', 'w', encoding='utf8') as f:
            f.write(text.strip())

    logging.info('OK. Отчеты успешно сформированы.')


if __name__ == '__main__':
    main()
