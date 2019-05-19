import subprocess
import sys

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

install('flask')
install('python-dotenv')
install('flask-wtf')
install('flask-sqlalchemy')
install('flask-migrate')
install('flask-login')
install('flask-mail')
install('pyjwt')
install('flask-bootstrap')
install('flask-bs4')
