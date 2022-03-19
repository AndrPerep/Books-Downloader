import argparse
import requests

from parse_tululu import download_image
from parse_tululu import download_text
from parse_tululu import get_soup
from parse_tululu import parse_book_page
from pprint import pprint


def create_parser():
    parser = argparse.ArgumentParser(description='Скачивает книги с сайта tululu.org в заданном диапазоне ID.')
    parser.add_argument('-s', '--start_id', help='ID первой книги для скачивания', type=int, default=1)
    parser.add_argument('-e', '--end_id', help='ID последней книги для скачивания', type=int, default=10)

    return parser


def main():
    txt_base_url = 'http://tululu.org/txt.php'
    books_folder = 'books/'
    img_folder = 'pictures/'

    parser = create_parser()
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id+1):
        try:
            url = f'http://tululu.org/b{book_id}/'
            soup = get_soup(url)
            book = parse_book_page(soup, book_id)
            pprint(book)

            download_text(txt_base_url, book['book_filename'], books_folder, book_id)
            download_image(book['img_url'], book['img_filename'], img_folder)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
