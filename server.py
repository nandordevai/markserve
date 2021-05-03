import codecs
import os
import shutil
from functools import reduce

import markdown
from markdown.extensions.toc import TocExtension
from flask import Flask, render_template, url_for, redirect, abort, send_from_directory, Response

app = Flask(__name__)
debug = True
app.config.update(
    DATADIR='data',
    DEBUG=debug,
    EXPORTDIR='export',
)
tags = {}


def url_builder(urlo, base, end, url_whitespace, url_case):
    return urlo.path


def url_builder_export(urlo, base, end, url_whitespace, url_case):
    return urlo.path + '.html'


md_config = {
    'mdx_wikilink_plus': {
        'build_url': url_builder,
    },
}

md_config_export = {
    'mdx_wikilink_plus': {
        'build_url': url_builder_export,
    },
}


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
        current_dir = '' if folders == ['data'] else folders[-1]
        subdir = dict.fromkeys([os.path.join(current_dir, f[:-3])
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


def export_file(path):
    root = '../' if '/' in path else './'
    source = os.path.join(app.config['DATADIR'], '{}.md'.format(path))
    destination = codecs.open(os.path.join(
        app.config['EXPORTDIR'], '{}.html'.format(path)), 'w', 'utf-8')
    if not os.path.exists(source):
        abort(404)
    try:
        md_content = codecs.open(source, 'r', 'utf-8').read()
    except IOError:
        abort(500)
    html = markdown.markdown(md_content, extensions=[
                             TocExtension(toc_depth='2-4'),
                             'tables', 'meta', 'md_in_html', 'sane_lists',
                             'mdx_wikilink_plus'],
                             extension_configs=md_config_export)
    destination.write(render_template('page-export.html', title='test', content=html,
                                      pages=get_tree(), tags=get_tags(), root=root))


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('show_page', page='Index'))


@app.route('/<page>', defaults={'folder': ''}, methods=['GET'])
@app.route('/<folder>/<page>', methods=['GET'])
def show_page(folder, page):
    file = get_filename(folder, page)
    if not os.path.exists(file):
        abort(404)
    try:
        content = codecs.open(file, 'r', 'utf-8').read()
    except IOError:
        abort(500)
    html = markdown.markdown(content, extensions=[
                             TocExtension(toc_depth='2-4'),
                             'tables', 'meta', 'md_in_html', 'sane_lists',
                             'mdx_wikilink_plus'],
                             extension_configs=md_config)
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


@app.route('/export', methods=['GET'])
def export_all():
    if not os.path.exists(app.config['EXPORTDIR']):
        os.mkdir(app.config['EXPORTDIR'])
        os.mkdir(os.path.join(app.config['EXPORTDIR'], 'static'))
    shutil.copy('static/main.css',
                os.path.join(app.config['EXPORTDIR'], 'static'))
    shutil.copy('static/app.js',
                os.path.join(app.config['EXPORTDIR'], 'static'))
    shutil.copy('static/handouts.js',
                os.path.join(app.config['EXPORTDIR'], 'static'))
    shutil.copytree(os.path.join(app.config['DATADIR'], 'images'),
                    os.path.join(app.config['EXPORTDIR'], 'images'))
    for folder, files in get_tree().items():
        if files is not None:
            os.mkdir(os.path.join(app.config['EXPORTDIR'], folder))
            [export_file(f) for f in files.keys()]
        else:
            export_file(folder)
    return Response(status=200)


if __name__ == '__main__':
    build_tag_db()
    app.run(host='localhost')
