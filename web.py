import json
import random
from collections import namedtuple
from datetime import datetime, timedelta

from flask import Flask, redirect, render_template, url_for

app = Flask(__name__)


CACHE = {}
CacheEntry = namedtuple('CacheEntry', ['value', 'expire_at'])


def cache(key, expire_seconds):
    """Cache value returned by function for expire_seconds seconds"""
    def inner(fn):
        def wrapper(*args, **kwargs):
            cached = CACHE.get(key)
            if cached and cached.expire_at > datetime.now():
                return cached.value
            expire_at = datetime.now() + timedelta(seconds=expire_seconds)
            cached = CacheEntry(fn(*args, **kwargs), expire_at)
            CACHE[key] = cached
            return cached.value
        return wrapper
    return inner


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bg.jpg')
@cache('bg', 60)
def random_background():
    """Redirect to random background image chosen from directory"""
    try:
        with open('./urls.json') as f:
            urls = json.loads(f.read())
    except IOError:
        # Fallback
        return redirect(url_for('static', filename='images/background.jpg'))
    url = random.choice(urls)
    return redirect(url)


if __name__ == "__main__":
    app.run(debug=True)
