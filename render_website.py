import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    for page, page_books in enumerate(page_grouped_books):
        col_grouped_books = list(chunked(page_books, 2))

        template = env.get_template('template.html')
        rendered_page = template.render(books=col_grouped_books)

        page_file_name = os.path.join(pages_folder, f'index{page}.html')
        with open(page_file_name, 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print('Site rebuilt')


if __name__ == '__main__':
    txt_folder = 'books/'
    img_folder = 'pictures/'
    pages_folder = 'pages/'
    os.makedirs(pages_folder, exist_ok=True)

    with open('books.json', 'r', encoding='utf-8') as books_file:
        books_json = books_file.read()
    books = json.loads(books_json)

    for book in books:
        book['img_filepath'] = os.path.join(img_folder, book['img_filename'])
        book['txt_filepath'] = os.path.join(txt_folder, book['book_filename'])
    page_grouped_books = list(chunked(books, 10))


    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
