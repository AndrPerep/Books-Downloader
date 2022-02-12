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


def get_book_data(soup):
    title_text = soup.find('h1').text
    name, author = str(title_text).split('::')
    name = name.strip()
    book_filename = f'{id}. {name}.txt'
    payload = {
        'id': str(id)
    }
    return book_filename, payload


def get_img_data(soup):
    base_url = 'http://tululu.org'

    img_tag = soup.find('div', class_='bookimage').find('img')['src']
    img_url = urljoin(base_url, img_tag)
    img_filename = unquote(img_url.split('/')[-1])

    return img_filename, img_url


def get_comments(soup):
    comments = soup.find_all('div', class_='texts')
    comments_texts = []
    for comment in comments:
        comment_text = comment.find('span').text
        comments_texts.append(comment_text)

    return comments_texts

def download_file(url, filename, folder, payload):
    response = requests.get(url, params=payload, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    sanitazed_filename = sanitize_filename(filename)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, sanitazed_filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    books_url = 'http://tululu.org/txt.php'
    books_folder = 'books/'
    img_folder = 'pictures/'

    for id in range(0, 11):
        try:
            soup = get_soup(id)
            book_filename, payload = get_book_data(soup)
            img_filename, img_url = get_img_data(soup)
            comments = get_comments(soup)
            print(book_filename)
            pprint(comments)

            download_file(books_url, book_filename, books_folder, payload)
            download_file(img_url, img_filename, img_folder, payload)
        except:
            print('error')
