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


def get_soup(id):
    url = f'http://tululu.org/b{id}/'
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')


def get_img_data(soup):
    base_url = 'http://tululu.org'

    img_tag = soup.find('div', class_='bookimage').find('img')['src']
    img_url = urljoin(base_url, img_tag)
    img_filename = unquote(img_url.split('/')[-1])

    return img_filename, img_url


def download_file(url, filename, folder, payload):
    response = requests.get(url, params=payload, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    sanitazed_filename = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, sanitazed_filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(soup):
    book = {}

    title_text = soup.find('h1').text
    name, author = str(title_text).split('::')
    stripped_name = name.strip()
    stripped_author = author.strip()
    book_filename = f'{id}. {stripped_name}.txt'
    payload = {
        'id': str(id)
    }
    book['Заголовок'] = stripped_name
    book['Автор'] = stripped_author

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

    return book, book_filename, payload


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

    for id in range(args.start_id, args.end_id+1):
        try:
            soup = get_soup(id)
            book, book_filename, payload = parse_book_page(soup)
            img_filename, img_url = get_img_data(soup)
            pprint(book)

            download_file(books_url, book_filename, books_folder, payload)
            download_file(img_url, img_filename, img_folder, payload)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()