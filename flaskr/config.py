import os 

Download_PATH = 'wkhtmltopdf/bin/wkhtmltopdf.exe'
basedir = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
Download_FOLDER = os.path.join(APP_ROOT, Download_PATH)



class BaseConfig(object):
    """Base configuration."""
    #DADOS DA EMPRESA
    EMPRESA_RSOC ='Salete Torres de Araujo'
    EMPRESA_NOMFAN ='Porto Turismo'
    EMPRESA_CNPJ = '00.000.000/0001-00'
    EMPRESA_LOGRADOURO = 'Rua Padre Carapuceiro'
    EMPRESA_NUMLOGR = '821'
    EMPRESA_COMPLEMENTO = 'APTO 1501'
    EMPRESA_BAIRRO = 'Boa Viagem'
    EMPRESA_CODMUN = '11111'
    EMPRESA_CODUF = '27'
    EMPRESA_CODPAIS = '55'
    #CONFIDENCIAL
    SECRET_KEY='dev',
    SECURITY_PASSWORD_SALT='dev_two',
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    #BANCO DE DADOS
    TYPE_CONNECT = 'mysql'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
#    MYSQL_CONNECT='mysql://ptarsoneves:Strolandia1@database-1.cizel514jz3i.us-east-2.rds.amazonaws.com/flask_layout'
    MYSQL_CONNECT = 'mysql://root@localhost/flask_ancorar'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASS = ''
    MYSQL_PORT = '3306'
    MYSQL_DATABASE = 'flask_ancorar'
    SQLITE_CONNECT = 'sqlite:///' + os.path.join(basedir, 'dev.sqlite')
    #CORRESPONDENCIA
    MAIL_SERVER='smtp.office365.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_DEFAULT_SENDER="ptarsoneves@outlook.com",
    MAIL_USERNAME='ptarsoneves@outlook.com',
    MAIL_PASSWORD='xygqlnwsascfrrdi'

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev.sqlite')
    DEBUG_TB_ENABLED = True


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/example'
    DEBUG_TB_ENABLED = False
    STRIPE_SECRET_KEY = 'foo'
    STRIPE_PUBLISHABLE_KEY = 'bar'
