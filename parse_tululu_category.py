import argparse
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
    title_selector = 'h1'
    title_text = soup.select_one(title_selector).text
    name, author = str(title_text).split('::')
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


def download_text(filename, folder, book_id):
    url = 'http://tululu.org/txt.php'
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


def create_parser():
    parser = argparse.ArgumentParser(description='Скачивает книги с сайта tululu.org из определённой категории')
    parser.add_argument('-c', '--category', help='Категория книг. Можно найти в адресе страницы категории — например, "l55" или "biznes"', type=str, default='l55')
    parser.add_argument('-s', '--start_page', help='ID первой страницы для скачивания', type=int, default=1)
    parser.add_argument('-e', '--end_page', help='ID последней страницы для скачивания', type=int, default=10)
    parser.add_argument('-df', '--dest_folder', help='путь к каталогу с результатам парсинга: картинкам, книгам, информации', type=str, default='./')
    parser.add_argument('--skip_txt', help='не скачивать книги', action='store_const', const=False)
    parser.add_argument('--skip_imgs', help='не скачивать обложки книг', action='store_const', const=False)
    parser.add_argument('-j', '--json_path', help='путь к .json файлу с результатами')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    books = []
    dest_folder = args.dest_folder
    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    books_folder = os.path.join(dest_folder, 'books/')
    img_folder = os.path.join(dest_folder, 'pictures/')
    category_url = f'http://tululu.org/{args.category}/'


    for page in (args.start_page, args.end_page+1):
        category_page_base_url = f'http://tululu.org/{args.category}/{page}'
        category_page_soup = get_soup(category_url)
        tags = category_page_soup.find_all('table', class_='d_book')
        for tag in tags:
            id_selector = 'a'
            book_id = tag.select_one(id_selector)['href']
            book_url = urljoin(category_page_base_url, book_id)

            try:
                book_page_soup = get_soup(book_url)
                book = parse_book_page(book_page_soup, book_id)
                books.append(book)

                if not args.skip_txt:
                    download_text(book['book_filename'], books_folder, book_id)
                if not args.skip_imgs:
                    download_image(book['img_url'], book['img_filename'], img_folder)
            except requests.HTTPError:
                pass

    json_path = os.path.join(args.json_path, 'books.json')
    with open(json_path, 'w', encoding='utf8') as file:
        json.dump(books, file, ensure_ascii=False)


if __name__ == '__main__':
    main()