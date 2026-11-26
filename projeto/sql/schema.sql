-- ============================================================
-- Chefy · Esquema da base de dados (MySQL / MariaDB)
-- Importar no phpMyAdmin (separador "Importar") ou com:
--   mysql -u utilizador -p nome_da_bd < sql/schema.sql
-- Em local, criar antes a BD:
--   CREATE DATABASE chefy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- ============================================================

SET NAMES utf8mb4;

-- Ordem inversa de dependências, para poder reimportar o ficheiro.
DROP TABLE IF EXISTS receita_ingredientes;
DROP TABLE IF EXISTS receitas;
DROP TABLE IF EXISTS ingredientes;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS utilizadores;

-- Quem usa a aplicação.
CREATE TABLE utilizadores (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,            -- NUNCA a palavra-passe em claro
    perfil        ENUM('chef','cozinheiro') NOT NULL DEFAULT 'chef',
    criado_em     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_utilizadores_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Lista fixa de categorias de ingredientes (1 categoria -> N ingredientes).
CREATE TABLE categorias (
    id   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_categorias_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inventário da cozinha.
CREATE TABLE ingredientes (
    id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome           VARCHAR(100) NOT NULL,
    categoria_id   INT UNSIGNED NOT NULL,
    unidade        ENUM('kg','g','L','ml','un') NOT NULL DEFAULT 'kg',
    stock_atual    DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_minimo   DECIMAL(10,2) NOT NULL DEFAULT 0,  -- abaixo disto há "stock baixo"
    custo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,  -- € por unidade
    criado_por     INT UNSIGNED NULL,
    criado_em      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_ingredientes_nome (nome),
    KEY idx_ingredientes_categoria (categoria_id),
    CONSTRAINT fk_ingredientes_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ingredientes_utilizador
        FOREIGN KEY (criado_por) REFERENCES utilizadores (id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_ingredientes_valores
        CHECK (stock_atual >= 0 AND stock_minimo >= 0 AND custo_unitario >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Livro de receitas.
CREATE TABLE receitas (
    id                   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    titulo               VARCHAR(150) NOT NULL,
    descricao            VARCHAR(500) NULL,
    porcoes              SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    tempo_preparacao_min SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    instrucoes           TEXT NULL,
    criado_por           INT UNSIGNED NULL,
    criado_em            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_receitas_titulo (titulo),
    CONSTRAINT fk_receitas_utilizador
        FOREIGN KEY (criado_por) REFERENCES utilizadores (id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_receitas_valores CHECK (porcoes >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de ligação N:M — que ingredientes (e quanto) leva cada receita.
-- A quantidade está na unidade do ingrediente (ex.: 0,5 kg de farinha).
CREATE TABLE receita_ingredientes (
    receita_id     INT UNSIGNED NOT NULL,
    ingrediente_id INT UNSIGNED NOT NULL,
    quantidade     DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (receita_id, ingrediente_id),        -- não repete o mesmo ingrediente
    KEY idx_ri_ingrediente (ingrediente_id),
    CONSTRAINT fk_ri_receita
        FOREIGN KEY (receita_id) REFERENCES receitas (id)
        ON DELETE CASCADE ON UPDATE CASCADE,         -- apagar receita apaga as linhas
    CONSTRAINT fk_ri_ingrediente
        FOREIGN KEY (ingrediente_id) REFERENCES ingredientes (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,        -- não deixa apagar ingrediente em uso
    CONSTRAINT ck_ri_quantidade CHECK (quantidade > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
