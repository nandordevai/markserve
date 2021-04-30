import codecs
import os
from functools import reduce

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


def get_tree(rootdir=app.config['DATADIR']):
    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys([f[:-3] for f in files])
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir
    return dir[rootdir]


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
    return render_template('page.html', title=page, content=html, pages=get_tree())


if __name__ == '__main__':
    app.run(host='localhost')
