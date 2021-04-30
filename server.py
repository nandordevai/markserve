import markdown
import codecs
import os

from flask import Flask, render_template, url_for, redirect

app = Flask(__name__)
debug = True
app.config.update(
    DATADIR='data',
    IMGDIR='static/images',
    DEBUG=debug
)


def get_filename(page):
    return os.path.join(app.config['DATADIR'], page + '.md')


@ app.route('/', methods=['GET'])
def index():
    return redirect(url_for('show_page', page='Index'))


@ app.route('/<page>', methods=['GET'])
def show_page(page):
    try:
        content = codecs.open(get_filename(page), 'r', 'utf-8').read()
    except IOError:
        content = None
    # , pages=get_pages())
    html = markdown.markdown(content, extensions=['wikilinks'])
    return render_template('page.html', title=page, content=html)


if __name__ == '__main__':
    app.run(host='localhost')
