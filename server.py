import codecs
import os

import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from flask import Flask, render_template, url_for, redirect, abort

app = Flask(__name__)
debug = True
app.config.update(
    DATADIR='data',
    IMGDIR='static/images',
    DEBUG=debug
)


def get_filename(page):
    return os.path.join(app.config['DATADIR'], page.replace('_', ' ') + '.md')


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
                             WikiLinkExtension(end_url='')])
    return render_template('page.html', title=page, content=html)


if __name__ == '__main__':
    app.run(host='localhost')
