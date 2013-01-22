import os

from flask import Flask
from flask import render_template
from jinja2 import evalcontextfilter, Markup, escape
from jinja2.environment import Environment

#
# Custom filters for Jinja
#
@evalcontextfilter
def format_tags(eval_ctx, value, attr=''):
    f = lambda x: '<span class="tag %s">%s</span>' % (attr, x)

    if isinstance(value, list):
        return Markup(' '.join(map(f, value)))
    else:
        return Markup(f(value))

app = Flask(__name__)
app.jinja_env.filters['format_tags'] = format_tags

#
# Request handlers
#
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tag/<tag>")
def category(tag):
    from pymongo import MongoClient
    import settings

    connection = MongoClient(settings.DB_URL, settings.DB_PORT)
    db = connection.resume
    db.authenticate(settings.DB_USERNAME, settings.DB_PASSWORD)

    # http://docs.mongodb.org/manual/reference/operator/or/#_S_or
    projects = db.projects.find({'$or': [{'keywords':tag}, {'languages':tag}, {'year':int(tag)}]})

    return render_template("projects.html", projects=projects)

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 80))
    debug = bool(os.environ.get("DEBUG", 1))

    app.run(host=host, port=port, debug=debug)

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })
