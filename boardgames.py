from app import app, db
from app.models import User, Poll


# import shell context processor to make it easier to use python shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Poll': Poll}