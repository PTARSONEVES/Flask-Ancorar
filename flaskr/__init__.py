import os
from flask import Flask
from . import config

def create_app(test_config=None):
    #cria e configura o app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY = config.BaseConfig.SECRET_KEY,
        SECURITY_PASSWORD_SALT = config.BaseConfig.SECURITY_PASSWORD_SALT
    )

    from .controller.auth import auth
    app.register_blueprint(auth.bp)

    from .controller.start import start
    app.register_blueprint(start.bp)

    from .controller.blog import blog
    app.register_blueprint(blog.bp)

    from .controller.pdf import pdf
    app.register_blueprint(pdf.bp)

    if test_config is None:
        #Carrega a instância config, se ela existir, então não testa
        app.config.from_pyfile('config.py', silent=True)
    else:
        #Senão, carrega a estrutura de teste
        app.config.from_mapping(test_config)

    #Verifica se a pasta da instância existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .database import db
    db.init_app(app)

    app.add_url_rule('/', endpoint='home')
    app.add_url_rule('/register', endpoint='register')
#    app.add_url_rule('/', endpoint='index')

    return app