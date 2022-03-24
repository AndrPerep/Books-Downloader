import requests
import os
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import unquote
from pathvalidate import sanitize_filename
from pathlib import Path


def check_for_redirect(response):
    for i in response.history:
        if i.status_code == 302:
            raise requests.HTTPError


def get_soup(url):
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')


def parse_book_page(soup, book_id):
    title_selector = 'h1'
    title_text = soup.select_one(title_selector).text
    print(title_text)
    name, author = title_text.split('::')
    stripped_name = name.strip()
    stripped_author = author.strip()
    book_filename = sanitize_filename(f'{book_id}. {stripped_name}.txt')

    book = {
        'Заголовок': stripped_name,
        'Автор': stripped_author,
        'book_filename': book_filename
    }

    genres_selector = 'span.d_book a'
    genres_tag = soup.select(genres_selector)
    book['Жанры'] = [genre.text for genre in genres_tag]

    comments = soup.find_all('div', class_='texts')
    book['Комментарии'] = [comment.find('span').text for comment in comments]

    base_url = 'http://tululu.org'
    img_selector = 'div.bookimage img'
    img_tag = soup.select_one(img_selector)['src']
    img_url = urljoin(base_url, img_tag)
    book['img_url'] = img_url
    book['img_filename'] = sanitize_filename(unquote(img_url.split('/')[-1]))

    return book


def download_text(url, filename, folder, book_id):
    payload = {
        'id': book_id
    }
    response = requests.get(url, params=payload, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    sanitazed_filename = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, sanitazed_filename)

    with open(filepath, 'w') as file:
        file.write(response.text)


def download_image(url, filename, folder):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)


def save_json(books, json_path='./'):
    json_path = os.path.join(json_path, 'books.json')
    with open(json_path, 'w', encoding='utf8') as file:
        json.dump(books, file, ensure_ascii=False)
