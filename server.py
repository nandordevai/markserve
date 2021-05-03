import codecs
import os
from functools import reduce

import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from markdown.extensions.toc import TocExtension
from flask import Flask, render_template, url_for, redirect, abort, send_from_directory

app = Flask(__name__)
debug = True
app.config.update(
    DATADIR='data',
    DEBUG=debug
)
tags = {}


def get_filename(folder, page):
    return os.path.join(app.config['DATADIR'], folder, '{}.md'.format(page))


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
        if path.endswith('/images'):
            continue
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys([os.path.join(folders[-1], f[:-3])
                               for f in files if not f.startswith('.')])
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir
    return dir[rootdir]


def get_pages():
    return [file[:-3]
            for file in sorted(os.listdir(app.config['DATADIR']))
            if file.endswith('.md')]


def get_tags():
    return tags.keys()


def get_pages_for_tag(tag):
    return tags[tag]


def build_tag_db():
    for file in os.listdir(app.config['DATADIR']):
        if file.endswith('.md'):
            content = codecs.open(os.path.join(
                app.config['DATADIR'], file), 'r', 'utf-8').read()
            md = markdown.Markdown(extensions=['meta'])
            md.convert(content)
            if 'tags' in md.Meta:
                for tag in md.Meta['tags']:
                    tags.setdefault(tag, [])
                    tags[tag].append(file[:-3])


def url_builder(label, base, end):
    return label


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('show_page', page='Index'))


@app.route('/<page>', defaults={'folder': ''}, methods=['GET'])
@app.route('/<folder>/<page>', methods=['GET'])
def show_page(folder, page):
    file = get_filename(folder, page)
    print(file)
    if not os.path.exists(file):
        abort(404)
    try:
        content = codecs.open(file, 'r', 'utf-8').read()
    except IOError:
        abort(500)
    html = markdown.markdown(content, extensions=[
                             WikiLinkExtension(
                                 end_url='', build_url=url_builder),
                             TocExtension(toc_depth='2-4'),
                             'tables', 'meta', 'md_in_html', 'sane_lists',
                             'mdx_wikilink_plus'])
    return render_template('page.html', title=page, content=html,
                           pages=get_tree(), tags=get_tags())


@app.route('/images/<filename>', methods=['GET'])
def send_image(filename):
    return send_from_directory(os.path.join(app.config['DATADIR'], 'images'), filename)


@app.route('/tag/<tag>', methods=['GET'])
def show_tags(tag):
    return render_template('tag.html', title='Tag: {}'.format(tag),
                           tag=tag, pages=get_pages_for_tag(tag), tags=get_tags(),
                           all_pages=get_pages())


@app.route('/handouts', methods=['GET'])
def handouts():
    return render_template('handouts.html')


if __name__ == '__main__':
    build_tag_db()
    app.run(host='localhost')
