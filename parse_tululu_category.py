import argparse
import requests
import os

from parse_tululu import download_image
from parse_tululu import download_text
from parse_tululu import get_soup
from parse_tululu import parse_book_page
from parse_tululu import save_json
from urllib.parse import urljoin
from pathlib import Path


def get_last_page(soup):
    last_page_selector = 'p.center a.npage'
    last_page = soup.select(last_page_selector)[-1].text

    return int(last_page)


def create_parser():
    parser = argparse.ArgumentParser(description='Скачивает книги с сайта tululu.org из определённой категории')
    parser.add_argument('-c', '--category', help='Категория книг. Можно найти в адресе страницы категории — например, "l55" или "biznes"', type=str, default='l55')
    parser.add_argument('-s', '--start_page', help='ID первой страницы для скачивания', type=int, default=1)
    parser.add_argument('-e', '--end_page', help='ID последней страницы для скачивания', type=int)
    parser.add_argument('-df', '--dest_folder', help='путь к каталогу с результатам парсинга: картинкам, книгам, информации', type=str, default='./')
    parser.add_argument('--skip_txt', help='не скачивать книги', action='store_const', const=True, default=False)
    parser.add_argument('--skip_imgs', help='не скачивать обложки книг', action='store_const', const=True, default=False)
    parser.add_argument('-j', '--json_path', help='путь к .json файлу с результатами', type=str, default='./')

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
    txt_base_url = 'http://tululu.org/txt.php'

    if args.end_page:
        last_page = args.end_page
    else:
        last_page = get_last_page(get_soup(category_url))

    for page in (args.start_page, last_page+1):
        category_page_url = f'http://tululu.org/{args.category}/{page}/'
        category_page_soup = get_soup(category_page_url)
        book_selector = 'table.d_book'
        book_tags = category_page_soup.select(book_selector)
        for book_tag in book_tags:
            id_selector = 'a'
            book_id = book_tag.select_one(id_selector)['href']
            book_url = urljoin(category_page_url, book_id)

            try:
                book_page_soup = get_soup(book_url)
                book = parse_book_page(book_page_soup, book_id)
                books.append(book)

                if not args.skip_txt:
                    download_text(txt_base_url, book['book_filename'], books_folder, book_id)
                if not args.skip_imgs:
                    download_image(book['img_url'], book['img_filename'], img_folder)
            except requests.HTTPError:
                pass

    save_json(books, args.json_path)


if __name__ == '__main__':
    main()
