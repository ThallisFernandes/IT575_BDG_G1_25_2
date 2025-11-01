-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema cadastro_imobiliario_it575
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema cadastro_imobiliario_it575
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `cadastro_imobiliario_it575` DEFAULT CHARACTER SET utf8 ;
USE `cadastro_imobiliario_it575` ;

-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`estado`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`estado` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `geometria` POLYGON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `nome_UNIQUE` (`nome` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`cidade`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`cidade` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_estado` INT NOT NULL,
  `nome` VARCHAR(100) NOT NULL,
  `geometria` POLYGON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_cidade_estado_idx` (`id_estado` ASC) VISIBLE,
  CONSTRAINT `fk_cidade_estado`
    FOREIGN KEY (`id_estado`)
    REFERENCES `cadastro_imobiliario_it575`.`estado` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`bairro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`bairro` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_cidade` INT NOT NULL,
  `nome` VARCHAR(150) NOT NULL,
  `geometria` POLYGON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_bairro_cidade1_idx` (`id_cidade` ASC) VISIBLE,
  CONSTRAINT `fk_bairro_cidade1`
    FOREIGN KEY (`id_cidade`)
    REFERENCES `cadastro_imobiliario_it575`.`cidade` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`tipo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`tipo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `descricao` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `descricao_UNIQUE` (`descricao` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`logradouro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`logradouro` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_tipo` INT NOT NULL,
  `nome` VARCHAR(45) NOT NULL,
  `geometria` MULTIPOINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_logradouro_tipo1_idx` (`id_tipo` ASC) VISIBLE,
  CONSTRAINT `fk_logradouro_tipo1`
    FOREIGN KEY (`id_tipo`)
    REFERENCES `cadastro_imobiliario_it575`.`tipo` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`endereco`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`endereco` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_bairro` INT NOT NULL,
  `logradouro_id` INT NULL,
  `cep` VARCHAR(45) NOT NULL,
  `numero` VARCHAR(45) NOT NULL,
  `geometria` VARCHAR(45) NOT NULL,
  `complemento` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_endereco_bairro1_idx` (`id_bairro` ASC) VISIBLE,
  INDEX `fk_endereco_logradouro1_idx` (`logradouro_id` ASC) VISIBLE,
  CONSTRAINT `fk_endereco_bairro1`
    FOREIGN KEY (`id_bairro`)
    REFERENCES `cadastro_imobiliario_it575`.`bairro` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_endereco_logradouro1`
    FOREIGN KEY (`logradouro_id`)
    REFERENCES `cadastro_imobiliario_it575`.`logradouro` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`imovel`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`imovel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_endereco` INT NOT NULL,
  `valor_venal` DOUBLE NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_imovel_endereco1_idx` (`id_endereco` ASC) VISIBLE,
  CONSTRAINT `fk_imovel_endereco1`
    FOREIGN KEY (`id_endereco`)
    REFERENCES `cadastro_imobiliario_it575`.`endereco` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`iptu`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`iptu` (
  `id_imovel` INT NOT NULL,
  `valor` DOUBLE NOT NULL,
  `status_pagamento` TINYINT NOT NULL,
  `data_pagamento` DATE NULL,
  `data_vencimento` DATE NULL,
  `hora_pagamento` VARCHAR(45) NULL,
  INDEX `fk_iptu_imovel1_idx` (`id_imovel` ASC) VISIBLE,
  PRIMARY KEY (`id_imovel`),
  CONSTRAINT `fk_iptu_imovel1`
    FOREIGN KEY (`id_imovel`)
    REFERENCES `cadastro_imobiliario_it575`.`imovel` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`terreno`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`terreno` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `testada` FLOAT NULL,
  `geometria` POLYGON NOT NULL,
  `area` DOUBLE NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`edificacao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`edificacao` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_terreno` INT NULL,
  `geometria` MULTIPOLYGON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_edificacao_terreno1_idx` (`id_terreno` ASC) VISIBLE,
  CONSTRAINT `fk_edificacao_terreno1`
    FOREIGN KEY (`id_terreno`)
    REFERENCES `cadastro_imobiliario_it575`.`terreno` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`juridica`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`juridica` (
  `cnpj` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`cnpj`),
  UNIQUE INDEX `cnpj_UNIQUE` (`cnpj` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`proprietario_juridico`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`proprietario_juridico` (
  `id_imovel` INT NOT NULL,
  `cnpj` VARCHAR(45) NOT NULL,
  `razao_social` VARCHAR(255) NOT NULL,
  `data_criacao` DATE NULL,
  INDEX `fk_proprietario_juridico_imovel1_idx` (`id_imovel` ASC) VISIBLE,
  PRIMARY KEY (`cnpj`, `id_imovel`),
  UNIQUE INDEX `cnpj_UNIQUE` (`cnpj` ASC) VISIBLE,
  CONSTRAINT `fk_proprietario_juridico_imovel1`
    FOREIGN KEY (`id_imovel`)
    REFERENCES `cadastro_imobiliario_it575`.`imovel` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_proprietario_juridico_juridica1`
    FOREIGN KEY (`cnpj`)
    REFERENCES `cadastro_imobiliario_it575`.`juridica` (`cnpj`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`fisica`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`fisica` (
  `rg` VARCHAR(8) NOT NULL,
  PRIMARY KEY (`rg`),
  UNIQUE INDEX `rg_UNIQUE` (`rg` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`proprietario_fisico`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`proprietario_fisico` (
  `id_imovel` INT NOT NULL,
  `rg` VARCHAR(8) NOT NULL,
  `nome` VARCHAR(255) NOT NULL,
  `data_nascimento` DATE NULL,
  INDEX `fk_proprietario_fisico_imovel1_idx` (`id_imovel` ASC) VISIBLE,
  PRIMARY KEY (`rg`, `id_imovel`),
  UNIQUE INDEX `rg_UNIQUE` (`rg` ASC) VISIBLE,
  CONSTRAINT `fk_proprietario_fisico_imovel1`
    FOREIGN KEY (`id_imovel`)
    REFERENCES `cadastro_imobiliario_it575`.`imovel` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_proprietario_fisico_fisica1`
    FOREIGN KEY (`rg`)
    REFERENCES `cadastro_imobiliario_it575`.`fisica` (`rg`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`pessoa`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`pessoa` (
  `id` INT NOT NULL,
  `id_fisica` VARCHAR(8) NOT NULL,
  `id_juridica` VARCHAR(45) NOT NULL,
  `cpf` VARCHAR(11) NOT NULL,
  PRIMARY KEY (`id`, `id_fisica`, `id_juridica`),
  UNIQUE INDEX `cpf_UNIQUE` (`cpf` ASC) VISIBLE,
  INDEX `fk_pessoa_fisica1_idx` (`id_fisica` ASC) VISIBLE,
  INDEX `fk_pessoa_juridica1_idx` (`id_juridica` ASC) VISIBLE,
  CONSTRAINT `fk_pessoa_fisica1`
    FOREIGN KEY (`id_fisica`)
    REFERENCES `cadastro_imobiliario_it575`.`fisica` (`rg`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_pessoa_juridica1`
    FOREIGN KEY (`id_juridica`)
    REFERENCES `cadastro_imobiliario_it575`.`juridica` (`cnpj`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`bairro_logradouro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`bairro_logradouro` (
  `id_bairro` INT NOT NULL,
  `id_logradouro` INT NOT NULL,
  PRIMARY KEY (`id_bairro`, `id_logradouro`),
  INDEX `fk_bairro_has_logradouro_logradouro1_idx` (`id_logradouro` ASC) VISIBLE,
  INDEX `fk_bairro_has_logradouro_bairro1_idx` (`id_bairro` ASC) VISIBLE,
  CONSTRAINT `fk_bairro_has_logradouro_bairro1`
    FOREIGN KEY (`id_bairro`)
    REFERENCES `cadastro_imobiliario_it575`.`bairro` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_bairro_has_logradouro_logradouro1`
    FOREIGN KEY (`id_logradouro`)
    REFERENCES `cadastro_imobiliario_it575`.`logradouro` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`edificacao_imovel`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`edificacao_imovel` (
  `id_edificacao` INT NOT NULL,
  `id_imovel` INT NOT NULL,
  PRIMARY KEY (`id_edificacao`, `id_imovel`),
  INDEX `fk_edificacao_has_imovel_imovel1_idx` (`id_imovel` ASC) VISIBLE,
  INDEX `fk_edificacao_has_imovel_edificacao1_idx` (`id_edificacao` ASC) VISIBLE,
  CONSTRAINT `fk_edificacao_has_imovel_edificacao1`
    FOREIGN KEY (`id_edificacao`)
    REFERENCES `cadastro_imobiliario_it575`.`edificacao` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_edificacao_has_imovel_imovel1`
    FOREIGN KEY (`id_imovel`)
    REFERENCES `cadastro_imobiliario_it575`.`imovel` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`residencial`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`residencial` (
  `id_edificacao` INT NOT NULL,
  `piscina` INT NULL,
  `garagem` TINYINT NULL,
  `moradores` TINYINT NOT NULL,
  PRIMARY KEY (`id_edificacao`),
  CONSTRAINT `fk_residencial_edificacao1`
    FOREIGN KEY (`id_edificacao`)
    REFERENCES `cadastro_imobiliario_it575`.`edificacao` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`comercial`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`comercial` (
  `id_edificacao` INT NOT NULL,
  `descricao` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_edificacao`),
  INDEX `fk_comercial_edificacao1_idx` (`id_edificacao` ASC) VISIBLE,
  CONSTRAINT `fk_comercial_edificacao1`
    FOREIGN KEY (`id_edificacao`)
    REFERENCES `cadastro_imobiliario_it575`.`edificacao` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`casa`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`casa` (
  `id_residencial_edificacao` INT NOT NULL,
  `area_nao_construida` INT NOT NULL,
  PRIMARY KEY (`id_residencial_edificacao`),
  CONSTRAINT `fk_casa_residencial1`
    FOREIGN KEY (`id_residencial_edificacao`)
    REFERENCES `cadastro_imobiliario_it575`.`residencial` (`id_edificacao`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cadastro_imobiliario_it575`.`apartamento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`apartamento` (
  `id_residencial_edificacao` INT NOT NULL,
  `bloco` VARCHAR(3) NOT NULL,
  PRIMARY KEY (`id_residencial_edificacao`),
  INDEX `fk_apartamento_residencial1_idx` (`id_residencial_edificacao` ASC) VISIBLE,
  CONSTRAINT `fk_apartamento_residencial1`
    FOREIGN KEY (`id_residencial_edificacao`)
    REFERENCES `cadastro_imobiliario_it575`.`residencial` (`id_edificacao`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
