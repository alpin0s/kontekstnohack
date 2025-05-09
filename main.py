#!/usr/bin/env python3
"""
KontekstnoHack CLI
Получение challenge_id по room_id или напрямую, автоматическая отправка слов до решения.
Использование:
  python main.py --room ROOM_ID
  python main.py --challenge CHALLENGE_ID --word слово
"""
import requests
import random
import sys
import argparse

API_BASE = 'https://xn--80aqu.xn--e1ajbkccewgd.xn--p1ai'

def generate_user_id() -> str:
    """Сгенерировать случайный user_id"""
    suffix = random.randint(10**11, 10**12 - 1)
    return f'daab6d58-c8a5-498b-9045-{suffix}'

def api_get(endpoint: str, **params) -> dict:
    """Отправить GET-запрос к API и вернуть JSON"""
    url = f"{API_BASE}/{endpoint}"
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def get_challenge_id_from_room(room_id: str) -> str:
    """Получить challenge_id по room_id"""
    data = api_get('get_room', room_id=room_id)
    cid = data.get('challenge_id')
    if not cid:
        raise ValueError(f"Не найден challenge_id для room_id {room_id}")
    return cid

def solve_challenge(challenge_id: str, initial_word: str):
    """Инициализировать и автоматически отправлять подсказки."""
    user_id = generate_user_id()
    print(f'User ID: {user_id}')

    # Инициализация: отправляем начальное слово
    print(f'Отправляем начальное слово: {initial_word}')
    init_score = api_get(
        'get_score',
        challenge_id=challenge_id,
        user_id=user_id,
        word=initial_word,
        challenge_type='random'
    )
    print('Ответ:', init_score)

    attempts = []
    while True:
        tip = api_get(
            'get_tip',
            challenge_id=challenge_id,
            user_id=user_id,
            challenge_type='random'
        )
        word = tip.get('word', '')
        rank = tip.get('rank', -1)
        if not word:
            print('Получена пустая подсказка, прекращаю.')
            break
        print(f'Подсказка: {word} (rank={rank})')

        score = api_get(
            'get_score',
            challenge_id=challenge_id,
            user_id=user_id,
            word=word,
            challenge_type='random'
        )
        print('Ответ:', score)
        attempts.append((word, rank))

        if rank in (1, -1):
            break

    print('\nРезультаты:')
    for w, r in attempts:
        print(f'  {w} — rank {r}')

def main():
    parser = argparse.ArgumentParser(description='KontekstnoHack CLI')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--room', help='ID комнаты (room_id)')
    group.add_argument('--challenge', help='ID челленджа (challenge_id)')
    parser.add_argument('--word', default='человек', help='Начальное слово для get_score')
    args = parser.parse_args()

    try:
        if args.room:
            cid = get_challenge_id_from_room(args.room)
            print(f'Получен challenge_id: {cid}')
        else:
            cid = args.challenge
        solve_challenge(cid, args.word)
    except Exception as e:
        print('Ошибка:', e)
        sys.exit(1)

if __name__ == '__main__':
    main()
