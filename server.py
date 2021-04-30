import codecs
import os

import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from flask import Flask, render_template, url_for, redirect, abort

app = Flask(__name__)
debug = True
app.config.update(
    DATADIR='data',
    DEBUG=debug
)


def get_filename(page):
    return os.path.join(app.config['DATADIR'], page.replace('_', ' ') + '.md')


def add_file_entry(name):
    if name[-3:] == '.md':
        return {'name': name[:-3], 'children': None}
    else:
        return {'name': name, 'children': []}


def get_tree(start=app.config['DATADIR']):
    # os.walk() output:
    # /Users/nandi/Projects/Web/markserve/data ['things'] ['Index.md', 'wiki link.md']
    # /Users/nandi/Projects/Web/markserve/data/things [] ['one thing.md']
    # convert to:
    # [
    #   {
    #     'name': 'things',
    #     'children': [
    #       {
    #         'name': 'one thing',
    #         'children': None
    #       }
    #     ]
    #   },
    #   {
    #     'name': 'Index',
    #     'children': None
    #   },
    #   {
    #     'name': 'wiki link',
    #     'children': None
    #   }
    # ]
    items = []
    for root, dirs, files in os.walk(start):
        if len(dirs) > 0:
            for d in dirs:
                items.append({'name': d, 'children': get_tree(root)})
        if len(files) > 0:
            for f in files:
                items.append({'name': f, 'children': None})
    return items


def get_pages():
    return [add_file_entry(file)
            for file in sorted(os.listdir(app.config['DATADIR']))]


@ app.route('/', methods=['GET'])
def index():
    return redirect(url_for('show_page', page='Index'))


@ app.route('/<page>', methods=['GET'])
def show_page(page):
    file = get_filename(page)
    if not os.path.exists(file):
        abort(404)
    try:
        content = codecs.open(file, 'r', 'utf-8').read()
    except IOError:
        abort(500)
    html = markdown.markdown(content, extensions=[
                             WikiLinkExtension(end_url=''), 'tables'])
    return render_template('page.html', title=page, content=html, pages=get_pages())


if __name__ == '__main__':
    app.run(host='localhost')
