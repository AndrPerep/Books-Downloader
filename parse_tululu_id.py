import argparse
import requests

from parse_tululu import download_image
from parse_tululu import download_text
from parse_tululu import get_soup
from parse_tululu import parse_book_page
from parse_tululu import save_json


def create_parser():
    parser = argparse.ArgumentParser(description='Скачивает книги с сайта tululu.org в заданном диапазоне ID.')
    parser.add_argument('-s', '--start_id', help='ID первой книги для скачивания', type=int, default=1)
    parser.add_argument('-e', '--end_id', help='ID последней книги для скачивания', type=int, default=10)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    books = []
    txt_base_url = 'https://tululu.org/txt.php'
    books_folder = 'books/'
    img_folder = 'pictures/'

    for book_id in range(args.start_id, args.end_id+1):
        try:
            url = f'https://tululu.org/b{book_id}/'
            soup = get_soup(url)
            book = parse_book_page(soup, book_id)
            books.append(book)

            download_text(txt_base_url, book['book_filename'], books_folder, book_id)
            download_image(book['img_url'], book['img_filename'], img_folder)
        except requests.HTTPError:
            pass
    save_json(books)


if __name__ == '__main__':
    main()
