import sqlite3
import click, os

from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text
from flask import current_app, g
from ..config import BaseConfig

def get_db():
    typeconnect = BaseConfig.TYPE_CONNECT
    if 'db' not in g:
        if typeconnect == 'sqlite':
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
            print('USANDO SQLITE')
        if typeconnect == 'mysql':
            engine = create_engine(BaseConfig.MYSQL_CONNECT)
            g.db = engine.connect()
            print('USANDO MYSQL')
    return g.db

def close_db(e=None):
    db = g.pop('db',None)

    if db is not None:
        db.close()

def init_db():
    typeconnect = BaseConfig.TYPE_CONNECT
    db = get_db()

    if typeconnect == 'sqlite':
        with current_app.open_resource('database\schema.sql') as f:
            db.executescript(f.read().decode('utf8'))

    if typeconnect == 'mysql':
        init_mysql()

def init_mysql():
    db = get_db()
    """ Cria o Banco de Dados """
    query = text(
        f"DROP DATABASE IF EXISTS `flask_ancorar`;CREATE DATABASE IF NOT EXISTS `flask_ancorar` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci */;USE `flask_ancorar`;"
    )
    db.execute(query)
    """ Cria a tabela de tipo de Usuário """
    query = text(
        f"CREATE TABLE `user_class` (`id` INT(11) NOT NULL AUTO_INCREMENT,`class_name` VARCHAR(50) NOT NULL COLLATE 'utf8_general_ci',PRIMARY KEY (`id`) USING BTREE)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Cria a Tabela de Usuários"""
    query = text(
        f"CREATE TABLE `user` (`id` INT(11) NOT NULL AUTO_INCREMENT,`class_id` INT(11) NOT NULL DEFAULT 0,`username` VARCHAR(200) NOT NULL COLLATE 'utf8_general_ci',`email` VARCHAR(200) NOT NULL COLLATE 'utf8_general_ci',`email_verified_at` DATETIME NULL DEFAULT NULL,`email_confirmed` VARCHAR(1) NULL DEFAULT '0' COLLATE 'utf8_general_ci',`password` VARCHAR(200) NOT NULL DEFAULT '' COLLATE 'utf8_general_ci',`remember_token` TEXT NULL DEFAULT NULL COLLATE 'utf8_general_ci',`created_at` DATETIME NULL DEFAULT NULL,`updated_at` DATETIME NULL DEFAULT NULL,PRIMARY KEY (`id`) USING BTREE,INDEX `FK_user_user_class` (`class_id`) USING BTREE,CONSTRAINT `FK_user_user_class` FOREIGN KEY (`class_id`) REFERENCES `user_class` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Cria a Tabela de Referência para UFs e Municípios """
    query = text(
        f"CREATE TABLE dtf_municipios(uf_codigo VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',uf_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgint_codigo VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgint_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgimed_codigo VARCHAR(6) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgimed_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',mesoreg_codigo VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',mesoreg_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',microreg_codigo VARCHAR(3) NULL DEFAULT NULL COLLATE 'utf8_general_ci',microreg_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',municipio_codigo VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8_general_ci',municipio_codigo_amplo VARCHAR(7) NULL DEFAULT NULL COLLATE 'utf8_general_ci',municipio_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci')COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Carrega a tabela de referência com os dados do IBGE """
    query = text(
        f"LOAD DATA INFILE 'C:/Users/ptars/OneDrive/IBGE/DIVISAO_TERRITORIAL/RELATORIO_DTB_BRASIL_MUNICIPIO.csv' INTO TABLE dtf_municipios FIELDS TERMINATED BY ';';DELETE FROM dtf_municipios WHERE uf_codigo='UF';"
    )
    db.execute(query)
    """ Cria os tipos básicos de Usuários """
    query = text(
        f"INSERT INTO user_class (`class_name`) VALUES ('Administrador'),('Cliente'),('Visitante'),('Colaborador');"
    )
    db.execute(query)
    """ Cria o Administrador principal do Sistema """
    query = text(
        f"INSERT INTO user (`class_id`,`username`,`email`,`email_verified_at`,`email_confirmed`,`password`,`created_at`,`updated_at`) VALUES (:c1,:c2,:c3,:c4,:c5,:c6,:c7,:c8)"
    )
    db.execute(
        query,[{
            'c1' : 1,
            'c2' : 'ptarsoneves',
            'c3' : 'ptarsoneves@gmail.com',
            'c4' : datetime.now(),
            'c5' : '1',
            'c6' : generate_password_hash('admin'),
            'c7' : datetime.now(),
            'c8' : datetime.now()
        }]
    )
    """ Cria a Tabela de UFs """
    query = text(
        f"CREATE TABLE `ufs`(`id` INT(11) NOT NULL AUTO_INCREMENT,`uf_codigo` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',`uf_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',PRIMARY KEY (`id`) USING BTREE)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Cria a Tabela de Municípios """
    query = text(
        f"CREATE TABLE `municipios` (`id` INT(11) NOT NULL AUTO_INCREMENT,`ufs_id` INT(11) NOT NULL DEFAULT '0',`municipio_codigo` VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8_general_ci',`municipio_codigo_amplo` VARCHAR(7) NULL DEFAULT NULL COLLATE 'utf8_general_ci',`municipio_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',PRIMARY KEY (`id`) USING BTREE,INDEX `FK_municipios_ufs` (`ufs_id`) USING BTREE,CONSTRAINT `FK_municipios_ufs` FOREIGN KEY (`ufs_id`) REFERENCES `ufs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Insere os dados na tabela de UFs """
    query = text(
        f"INSERT INTO ufs (`uf_codigo`,`uf_nome`) SELECT DISTINCT a.uf_codigo,a.uf_nome FROM dtf_municipios a;"
    )
    db.execute(query)
    """ Insere os dados na Tabela de Municípios"""
    query = text(
        f"INSERT INTO municipios (`ufs_id`,`municipio_codigo`,`municipio_codigo_amplo`,`municipio_nome`) SELECT DISTINCT b.id AS ufs_id,a.municipio_codigo,a.municipio_codigo_amplo,a.municipio_nome FROM dtf_municipios a, ufs b WHERE a.uf_codigo=b.uf_codigo;"
    )
    db.execute(query)
    """ Elimina a tabela de referência """
    query = text(
        f"DROP TABLE if EXISTS dtf_municipios"
    )
    db.execute(query)
    """ Insere campos de criação e alteração de dados nas tabelas de Tipos de Usuário, UFs e Municípios """
    query = text(
        f"ALTER TABLE `ufs` ADD COLUMN `created_at` DATETIME NULL AFTER `uf_nome`,ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;ALTER TABLE `municipios` ADD COLUMN `created_at` DATETIME NULL AFTER `municipio_nome`,ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;ALTER TABLE `user_class` ADD COLUMN `created_at` DATETIME NULL AFTER `class_name`,ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;"
    )
    db.execute(query)
    """ Insere data de criação e atualização nas tabelas de tipo de usuario, ufs e municípios """
    query = text(
        f"UPDATE ufs SET created_at= :criacao, updated_at= :atualizacao;UPDATE municipios SET created_at= :criacao, updated_at= :atualizacao;UPDATE user_class SET created_at= :criacao, updated_at= :atualizacao"
    )
    db.execute(query,{'criacao':datetime.now(),'atualizacao':datetime.now()})
    """ Confirma """
    db.commit()

    result = "OK"
    return result

def init_mysql_aws():
    db = get_db()
    """ Cria o Banco de Dados """
    query = text(
        f"DROP DATABASE IF EXISTS `flask_ancorar`;CREATE DATABASE IF NOT EXISTS `flask_ancorar` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci */;USE `flask_ancorar`;"
    )
    db.execute(query)
    """ Cria a tabela de tipo de Usuário """
    query = text(
        f"CREATE TABLE `user_class` (`id` INT(11) NOT NULL AUTO_INCREMENT,`class_name` VARCHAR(50) NOT NULL COLLATE 'utf8_general_ci',PRIMARY KEY (`id`) USING BTREE)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Cria a Tabela de Usuários"""
    query = text(
        f"CREATE TABLE `user` (`id` INT(11) NOT NULL AUTO_INCREMENT,`class_id` INT(11) NOT NULL DEFAULT 0,`username` VARCHAR(200) NOT NULL COLLATE 'utf8_general_ci',`email` VARCHAR(200) NOT NULL COLLATE 'utf8_general_ci',`email_verified_at` DATETIME NULL DEFAULT NULL,`email_confirmed` VARCHAR(1) NULL DEFAULT '0' COLLATE 'utf8_general_ci',`password` VARCHAR(200) NOT NULL DEFAULT '' COLLATE 'utf8_general_ci',`remember_token` TEXT NULL DEFAULT NULL COLLATE 'utf8_general_ci',`created_at` DATETIME NULL DEFAULT NULL,`updated_at` DATETIME NULL DEFAULT NULL,PRIMARY KEY (`id`) USING BTREE,INDEX `FK_user_user_class` (`class_id`) USING BTREE,CONSTRAINT `FK_user_user_class` FOREIGN KEY (`class_id`) REFERENCES `user_class` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Cria a Tabela de Referência para UFs e Municípios """
    query = text(
        f"CREATE TABLE dtf_municipios(uf_codigo VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',uf_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgint_codigo VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgint_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgimed_codigo VARCHAR(6) NULL DEFAULT NULL COLLATE 'utf8_general_ci',rgimed_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',mesoreg_codigo VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',mesoreg_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',microreg_codigo VARCHAR(3) NULL DEFAULT NULL COLLATE 'utf8_general_ci',microreg_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',municipio_codigo VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8_general_ci',municipio_codigo_amplo VARCHAR(7) NULL DEFAULT NULL COLLATE 'utf8_general_ci',municipio_nome VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci')COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Carrega a tabela de referência com os dados do IBGE """
#    query = text(
#        f"LOAD DATA INFILE 'F:/OneDrive/IBGE/DIVISAO_TERRITORIAL/RELATORIO_DTB_BRASIL_MUNICIPIO.csv' INTO TABLE dtf_municipios FIELDS TERMINATED BY ';';DELETE FROM dtf_municipios WHERE uf_codigo='UF';"
#    )
#    db.execute(query)
    """ Cria os tipos básicos de Usuários """
    query = text(
        f"INSERT INTO user_class (`class_name`) VALUES ('Administrador'),('Cliente'),('Visitante'),('Colaborador');"
    )
    db.execute(query)
    """ Cria o Administrador principal do Sistema """
    query = text(
        f"INSERT INTO user (`class_id`,`username`,`email`,`email_verified_at`,`email_confirmed`,`password`,`created_at`,`updated_at`) VALUES (:c1,:c2,:c3,:c4,:c5,:c6,:c7,:c8)"
    )
    db.execute(
        query,[{
            'c1' : 1,
            'c2' : 'ptarsoneves',
            'c3' : 'ptarsoneves@gmail.com',
            'c4' : datetime.now(),
            'c5' : '1',
            'c6' : generate_password_hash('admin'),
            'c7' : datetime.now(),
            'c8' : datetime.now()
        }]
    )
    """ Cria a Tabela de UFs """
    query = text(
        f"CREATE TABLE `ufs`(`id` INT(11) NOT NULL AUTO_INCREMENT,`uf_codigo` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',`uf_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',PRIMARY KEY (`id`) USING BTREE)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Cria a Tabela de Municípios """
    query = text(
        f"CREATE TABLE `municipios` (`id` INT(11) NOT NULL AUTO_INCREMENT,`ufs_id` INT(11) NOT NULL DEFAULT '0',`municipio_codigo` VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8_general_ci',`municipio_codigo_amplo` VARCHAR(7) NULL DEFAULT NULL COLLATE 'utf8_general_ci',`municipio_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',PRIMARY KEY (`id`) USING BTREE,INDEX `FK_municipios_ufs` (`ufs_id`) USING BTREE,CONSTRAINT `FK_municipios_ufs` FOREIGN KEY (`ufs_id`) REFERENCES `ufs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE)COLLATE='utf8_general_ci'ENGINE=InnoDB;"
    )
    db.execute(query)
    """ Insere os dados na tabela de UFs 
    query = text(
        f"INSERT INTO ufs (`uf_codigo`,`uf_nome`) SELECT DISTINCT a.uf_codigo,a.uf_nome FROM dtf_municipios a;"
    )
    db.execute(query)"""
    """ Insere os dados na Tabela de Municípios
    query = text(
        f"INSERT INTO municipios (`ufs_id`,`municipio_codigo`,`municipio_codigo_amplo`,`municipio_nome`) SELECT DISTINCT b.id AS ufs_id,a.municipio_codigo,a.municipio_codigo_amplo,a.municipio_nome FROM dtf_municipios a, ufs b WHERE a.uf_codigo=b.uf_codigo;"
    )
    db.execute(query)"""
    """ Elimina a tabela de referência """
    query = text(
        f"DROP TABLE if EXISTS dtf_municipios"
    )
    db.execute(query)
    """ Insere campos de criação e alteração de dados nas tabelas de Tipos de Usuário, UFs e Municípios """
    query = text(
        f"ALTER TABLE `ufs` ADD COLUMN `created_at` DATETIME NULL AFTER `uf_nome`,ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;ALTER TABLE `municipios` ADD COLUMN `created_at` DATETIME NULL AFTER `municipio_nome`,ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;ALTER TABLE `user_class` ADD COLUMN `created_at` DATETIME NULL AFTER `class_name`,ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;"
    )
    db.execute(query)
    """ Insere data de criação e atualização nas tabelas de tipo de usuario, ufs e municípios """
    query = text(
        f"UPDATE ufs SET created_at= :criacao, updated_at= :atualizacao;UPDATE municipios SET created_at= :criacao, updated_at= :atualizacao;UPDATE user_class SET created_at= :criacao, updated_at= :atualizacao"
    )
    db.execute(query,{'criacao':datetime.now(),'atualizacao':datetime.now()})
    """ Confirma """
    db.commit()

    result = "OK"
    return result




@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('database inicializado.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

