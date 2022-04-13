import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server



def on_reload():
    template = env.get_template('template.html')
    rendered_page = template.render(books=books)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuilt")


if __name__ == '__main__':
    img_folder = 'pictures/'

    with open('books.json', 'r', encoding='utf-8') as books_file:
        books_json = books_file.read()
    books = json.loads(books_json)

    for book in books:
        book['img_filepath'] = os.path.join(img_folder, book['img_filename'])

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
