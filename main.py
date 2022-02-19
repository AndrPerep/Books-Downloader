import argparse
import requests
import os

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from pprint import pprint
from urllib.parse import urljoin
from urllib.parse import unquote


def check_for_redirect(response):
    if response.status_code in (301, 302):
        raise requests.HTTPError


def get_soup(book_id):
    url = f'http://tululu.org/b{book_id}/'
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')


def download_text(url, filename, folder, book_id):
    payload = {
        'id': str(book_id)
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

    sanitazed_filename = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, sanitazed_filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(soup, book_id):
    title_text = soup.find('h1').text
    name, author = str(title_text).split('::')
    stripped_name = name.strip()
    stripped_author = author.strip()
    book_filename = f'{book_id}. {stripped_name}.txt'

    book = {
        'Заголовок': stripped_name,
        'Автор': stripped_author
    }

    genres = []
    genres_tag = soup.find('span', class_='d_book').find_all('a')
    for genre in genres_tag:
        genres.append(genre.text)
    book['Жанры'] = genres

    comments_texts = []
    comments = soup.find_all('div', class_='texts')
    for comment in comments:
        comment_text = comment.find('span').text
        comments_texts.append(comment_text)
    book['Комментарии'] = comments_texts

    base_url = 'http://tululu.org'
    img_tag = soup.find('div', class_='bookimage').find('img')['src']
    img_url = urljoin(base_url, img_tag)
    img_filename = unquote(img_url.split('/')[-1])

    return img_filename, img_url

    return book, book_filename, img_filename, img_url


def create_parser():
    parser = argparse.ArgumentParser(description='Скачивает книги с сайта tululu.org в заданном диапазоне ID.')
    parser.add_argument('-s', '--start_id', help='ID первой книги для скачивания', type=int, default=1)
    parser.add_argument('-e', '--end_id', help='ID последней книги для скачивания', type=int, default=10)

    return parser


def main():
    books_url = 'http://tululu.org/txt.php'
    books_folder = 'books/'
    img_folder = 'pictures/'

    parser = create_parser()
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id+1):
        try:
            soup = get_soup(book_id)
            book, book_filename, img_filename, img_url = parse_book_page(soup, book_id)
            pprint(book)

            download_text(books_url, book_filename, books_folder, book_id)
            download_image(img_url, img_filename, img_folder)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
