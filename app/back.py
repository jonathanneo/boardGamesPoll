from flask import session, redirect, current_app
from flask import Flask
"""To be used in views.

Use `anchor` decorator to mark a view as a possible point of return.

`url()` is the last saved url.

Use `redirect` to return to the last return point visited.
"""
class back(object):
    app = Flask(__name__)
    cfg = app.config.get
    cookie = cfg('REDIRECT_BACK_COOKIE', 'back')
    default_view = cfg('REDIRECT_BACK_DEFAULT', 'index')

    @staticmethod
    def anchor(func, cookie=cookie):
        @functools.wraps(func)
        def result(*args, **kwargs):
            session[cookie] = request.url
            return func(*args, **kwargs)
        return result

    @staticmethod
    def url(default=default_view, cookie=cookie):
        return session.get(cookie, url_for(default))

    @staticmethod
    def redirect(default=default_view, cookie=cookie):
        return redirect(back.url(default, cookie))
