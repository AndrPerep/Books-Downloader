import requests
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import unquote
from pathvalidate import sanitize_filename
from pathlib import Path


def check_for_redirect(response):
    if response.status_code in (301, 302):
        raise requests.HTTPError


def get_soup(url):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')


def parse_book_page(soup, book_id):
    title_text = soup.find('h1').text
    name, author = str(title_text).split('::')
    stripped_name = name.strip()
    stripped_author = author.strip()
    book_filename = sanitize_filename(f'{book_id}. {stripped_name}.txt')

    book = {
        'Заголовок': stripped_name,
        'Автор': stripped_author,
        'book_filename': book_filename
    }

    genres_tag = soup.find('span', class_='d_book').find_all('a')
    book['Жанры'] = [genre.text for genre in genres_tag]

    comments = soup.find_all('div', class_='texts')
    book['Комментарии'] = [comment.find('span').text for comment in comments]

    base_url = 'http://tululu.org'
    img_tag = soup.find('div', class_='bookimage').find('img')['src']
    img_url = urljoin(base_url, img_tag)
    book['img_url'] = img_url
    book['img_filename'] = sanitize_filename(unquote(img_url.split('/')[-1]))

    return book


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

    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)


def main():
    books = []
    books_folder = 'books/'
    img_folder = 'pictures/'
    category_page_url = 'http://tululu.org/l55/'

    for page in range(1, 11):
        category_page_base_url = f'http://tululu.org/l55/{page}'
        category_page_soup = get_soup(category_page_url)
        tags = category_page_soup.find_all('table', class_='d_book')
        for tag in tags:
            book_id = tag.find('a')['href']
            book_url = urljoin(category_page_base_url, book_id)

            book_page_soup = get_soup(book_url)
            book = parse_book_page(book_page_soup, book_id)
            books.append(book)

            download_text(book_url, book['book_filename'], books_folder, book_id)
            download_image(book['img_url'], book['img_filename'], img_folder)

    with open("books.json", "w") as file:
        json.dump(books, file, ensure_ascii=False)


if __name__ == '__main__':
    main()
