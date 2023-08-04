#
# Inicializa o Banco de Dados
#
DROP DATABASE if EXISTS flask_ancorar;
CREATE DATABASE flask_ancorar;
USE flask_ancorar;
#
# Cria as tabelas referentes aos Usuários
#
CREATE TABLE `user_class` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`class_name` VARCHAR(50) NOT NULL COLLATE 'utf8_general_ci',
	`created_at` DATETIME NULL DEFAULT NULL,
	`updated_at` DATETIME NULL DEFAULT NULL,
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8_general_ci'
ENGINE=INNODB
;
CREATE TABLE `user` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`class_id` INT(11) NOT NULL DEFAULT 0,
	`username` VARCHAR(200) NOT NULL COLLATE 'utf8_general_ci',
	`email` VARCHAR(200) NOT NULL COLLATE 'utf8_general_ci',
	`email_verified_at` DATETIME NULL DEFAULT NULL,
	`email_confirmed` VARCHAR(1) NULL DEFAULT '0' COLLATE 'utf8_general_ci',
	`password` VARCHAR(200) NOT NULL DEFAULT '' COLLATE 'utf8_general_ci',
	`remember_token` TEXT NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`created_at` DATETIME NULL DEFAULT NULL,
	`updated_at` DATETIME NULL DEFAULT NULL,
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `FK_user_user_class` (`class_id`) USING BTREE,
	CONSTRAINT `FK_user_user_class` FOREIGN KEY (`class_id`) REFERENCES `user_class` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
)COLLATE='utf8_general_ci'
ENGINE=INNODB
;
INSERT INTO user_class (`class_name`,`created_at`,`updated_at`) VALUES ('Administrador',NOW(),NOW()),('Cliente',NOW(),NOW()),('Visitante',NOW(),NOW()),('Colaborador',NOW(),NOW());
INSERT INTO user (`class_id`,`username`,`email`,`email_verified_at`,`email_confirmed`,`password`,`created_at`,`updated_at`) 
	VALUES (1,'ptarsoneves','ptarsoneves@gmail.com',NOW(),'1','admin',NOW(),NOW());
#
# Cria as Tabelas de Uf´s e Municípios
#
CREATE TABLE `dtf_municipios`(
	`uf_codigo` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`uf_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`rgint_codigo` VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`rgint_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`rgimed_codigo` VARCHAR(6) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`rgimed_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`mesoreg_codigo` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`mesoreg_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`microreg_codigo` VARCHAR(3) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`microreg_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`municipio_codigo` VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`municipio_codigo_amplo` VARCHAR(7) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`municipio_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci'
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `dtf_siglas`(
	`uf_codigo` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`uf_sigla` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci'
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
LOAD DATA INFILE 'C:/Users/ptars/OneDrive/IBGE/CSV_TXT/UF_SIGLA.txt' INTO TABLE dtf_siglas FIELDS TERMINATED BY ';';
LOAD DATA INFILE 'C:/Users/ptars/OneDrive/IBGE/CSV_TXT/MUNICIPIOS.csv' INTO TABLE dtf_municipios FIELDS TERMINATED BY ';';
DELETE FROM dtf_municipios WHERE uf_codigo='UF';
DELETE FROM dtf_siglas WHERE uf_codigo='UF';
CREATE TABLE `ufs`(
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`uf_codigo` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`uf_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`uf_sigla` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8_general_ci'
ENGINE=INNODB
;
CREATE TABLE `municipios` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`ufs_id` INT(11) NOT NULL DEFAULT '0',
	`municipio_codigo` VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`municipio_codigo_amplo` VARCHAR(7) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`municipio_nome` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `FK_municipios_ufs` (`ufs_id`) USING BTREE,
	CONSTRAINT `FK_municipios_ufs` FOREIGN KEY (`ufs_id`) REFERENCES `ufs` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
)
COLLATE='utf8_general_ci'
ENGINE=INNODB
;
INSERT INTO ufs (`uf_codigo`,`uf_nome`,`uf_sigla`) SELECT DISTINCT a.uf_codigo,a.uf_nome,b.uf_sigla FROM dtf_municipios a, dtf_siglas b WHERE a.uf_codigo=b.uf_codigo;
INSERT INTO municipios (`ufs_id`,`municipio_codigo`,`municipio_codigo_amplo`,`municipio_nome`) 
	SELECT DISTINCT b.id AS ufs_id,a.municipio_codigo,a.municipio_codigo_amplo,a.municipio_nome FROM dtf_municipios a, ufs b WHERE a.uf_codigo=b.uf_codigo;
DROP TABLE dtf_municipios;
DROP TABLE dtf_siglas;
ALTER TABLE `ufs` 
	ADD COLUMN `created_at` DATETIME NULL AFTER `uf_sigla`,
	ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;
ALTER TABLE `municipios` 
	ADD COLUMN `created_at` DATETIME NULL AFTER `municipio_nome`,
	ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;
UPDATE ufs SET `uf_nome`=TRIM(`uf_nome`), created_at=NOW(), updated_at=NOW();
UPDATE municipios SET `municipio_nome`=TRIM(`municipio_nome`), created_at=NOW(), updated_at=NOW();
#
# Cria as Tabelas Relacionadas a dados Financeiros
#
CREATE TABLE `p_compensa` (
	`cnpjraiz` VARCHAR(8) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`compensacao` VARCHAR(3) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`nombanco` VARCHAR(200) NULL DEFAULT NULL COLLATE 'utf8_general_ci'
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `p_banco` (
	`cnpj_raiz` VARCHAR(8) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`nombanco` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci'
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `bancos` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`cnpjraiz` VARCHAR(8) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`nombanco` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `compensacao` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`id_banco` INT(11) NULL DEFAULT '0',
	`compensacao` VARCHAR(3) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `FK__bancos` (`id_banco`) USING BTREE,
	CONSTRAINT `FK__bancos` FOREIGN KEY (`id_banco`) REFERENCES `bancos` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `formapag` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`formapag` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`created_at` DATETIME NULL,
	`updated_at` DATETIME NULL,
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
LOAD DATA INFILE 'C:/Users/ptars/OneDrive/IBGE/CSV_TXT/COMPENSACAO.txt' INTO TABLE p_compensa FIELDS TERMINATED BY ';';
LOAD DATA INFILE 'C:/Users/ptars/OneDrive/IBGE/CSV_TXT/BANCOS.txt' INTO TABLE p_banco FIELDS TERMINATED BY ';';
INSERT INTO formapag (`formapag`,`created_at`,`updated_at`) VALUES ('Dinheiro',NOW(),NOW()),('PIX',NOW(),NOW()),('Cartão de Crédito',NOW(),NOW()),('Cartão de Débito',NOW(),NOW());
DELETE FROM p_compensa WHERE cnpjraiz LIKE'%xx%';
DELETE FROM p_banco WHERE cnpj_raiz LIKE'%x%' OR nombanco=NULL;
UPDATE p_banco SET nombanco=TRIM(nombanco);
INSERT INTO bancos (`cnpjraiz`,`nombanco`) SELECT DISTINCT * FROM p_banco ORDER BY CNPJ_RAIZ;
INSERT INTO compensacao (`compensacao`,`id_banco`) SELECT a.compensacao,b.id FROM p_compensa a, bancos b WHERE a.cnpjraiz=b.cnpjraiz ORDER BY a.compensacao;
DROP TABLE p_banco;
ALTER TABLE `bancos`
	ADD COLUMN `created_at` DATETIME NULL AFTER `nombanco`,
	ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;
ALTER TABLE `compensacao`
	ADD COLUMN `created_at` DATETIME NULL AFTER `compensacao`,
	ADD COLUMN `updated_at` DATETIME NULL AFTER `created_at`;
UPDATE bancos SET created_at=NOW(), updated_at=NOW();
UPDATE compensacao SET created_at=NOW(), updated_at=NOW();
CREATE TABLE prov SELECT a.*,'0' AS sit FROM p_compensa a;
ALTER TABLE `prov`
	CHANGE COLUMN `cnpjraiz` `cnpjraiz` VARCHAR(8) NOT NULL COLLATE 'utf8_general_ci' FIRST,
	ADD PRIMARY KEY (`cnpjraiz`);
DELETE FROM prov WHERE compensacao IS NULL;
REPLACE prov SELECT a.cnpjraiz,a.compensacao,a.nombanco,'1' AS sit FROM p_compensa a, bancos b WHERE a.cnpjraiz=b.cnpjraiz;
DELETE FROM prov WHERE sit='1';
INSERT INTO bancos (`cnpjraiz`,`nombanco`,`created_at`,`updated_at`) SELECT cnpjraiz,nombanco,NOW() AS created_at,NOW() AS updated_at FROM prov;
INSERT INTO compensacao (`id_banco`,`compensacao`,`created_at`,`updated_at`) SELECT a.id,b.compensacao,NOW() AS created_at,NOW() AS updated_at FROM bancos a, prov b WHERE a.cnpjraiz=b.cnpjraiz;
DROP TABLE p_compensa;
DROP TABLE prov;
