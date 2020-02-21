from datetime import datetime
import os
from functools import reduce

import requests

users = requests.get('https://json.medrating.org/users').json()
tasks = requests.get('https://json.medrating.org/todos').json()


def stringify(user_id):
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


if not os.path.exists('tasks'):
    os.mkdir('tasks')

for user in users:
    date = datetime.now()
    [complete, incomplete] = stringify(user['id'])

    text = f'''{user["name"]} <{user["email"]}> {date}
{user["company"]["name"]}

Завершенные задачи:
{complete}

Оставшиеся задачи:
{incomplete}
'''
    filename = f'tasks/{user["username"]}.txt'
    if os.path.exists(filename):
        with open(f'tasks/{user["username"]}_{date.strftime("%Y-%m-%dT%T")}.txt', 'w', encoding='utf8') as f:
            f.write(text)
    else:
        with open(f'tasks/{user["username"]}.txt', 'w', encoding='utf8') as f:
            f.write(text)
