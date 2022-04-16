import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from math import ceil
from more_itertools import chunked


def on_reload():
    page_grouped_books = list(chunked(books, books_on_page_num))
    last_page = ceil(len(books)/books_on_page_num)
    page_quantity = []
    for page_number in range(1, last_page+1):
        page_quantity.append(page_number)

    for page_index, books_on_page in enumerate(page_grouped_books):
        page = page_index+1
        page_filename = f'index{page}.html'
        page_path = os.path.join(pages_folder, page_filename)

        col_grouped_books = list(chunked(books_on_page, 2))
        template = env.get_template('template.html')
        rendered_page = template.render(
            books=col_grouped_books,
            current_page=page,
            page_quantity=page_quantity,
            page_filename=page_filename,
            last_page=last_page,
            prev_page=f'index{page-1}.html',
            next_page=f'index{page+1}.html'
        )
        with open(page_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print('Site rebuilt')


if __name__ == '__main__':
    txt_folder = 'books/'
    img_folder = 'pictures/'
    pages_folder = 'pages/'
    books_on_page_num = 10
    os.makedirs(pages_folder, exist_ok=True)

    with open('books.json', 'r', encoding='utf-8') as books_file:
        books_json = books_file.read()
    books = json.loads(books_json)

    for book in books:
        book['img_filepath'] = os.path.join('../', img_folder, book['img_filename'])
        book['txt_filepath'] = os.path.join('../', txt_folder, book['book_filename'])

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
