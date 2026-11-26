-- ============================================================
-- Chefy · Dados de exemplo (importar DEPOIS de schema.sql)
-- As categorias são necessárias; o resto serve para testar/demonstrar.
-- Os utilizadores criam-se pelo formulário de registo.
-- ============================================================

SET NAMES utf8mb4;

INSERT INTO categorias (nome) VALUES
    ('Carnes'), ('Peixe e marisco'), ('Legumes e fruta'), ('Lacticínios e ovos'),
    ('Mercearia'), ('Massas e farinhas'), ('Ervas e especiarias'), ('Bebidas'), ('Outros');

INSERT INTO ingredientes (nome, categoria_id, unidade, stock_atual, stock_minimo, custo_unitario) VALUES
    ('Farinha de trigo',  (SELECT id FROM categorias WHERE nome = 'Massas e farinhas'),    'kg', 12.00, 10.00,  0.90),
    ('Azeite virgem extra',(SELECT id FROM categorias WHERE nome = 'Mercearia'),            'L',   2.00,  5.00,  7.50),
    ('Ovos',              (SELECT id FROM categorias WHERE nome = 'Lacticínios e ovos'),    'un', 60.00, 30.00,  0.25),
    ('Manteiga',          (SELECT id FROM categorias WHERE nome = 'Lacticínios e ovos'),    'kg',  1.00,  4.00,  8.20),
    ('Leite',             (SELECT id FROM categorias WHERE nome = 'Lacticínios e ovos'),    'L',  10.00,  6.00,  0.85),
    ('Açúcar',            (SELECT id FROM categorias WHERE nome = 'Mercearia'),             'kg',  8.00,  5.00,  1.10),
    ('Cebola',            (SELECT id FROM categorias WHERE nome = 'Legumes e fruta'),       'kg',  7.50,  5.00,  1.20),
    ('Alho',              (SELECT id FROM categorias WHERE nome = 'Legumes e fruta'),       'kg',  0.80,  0.50,  6.00),
    ('Tomate',            (SELECT id FROM categorias WHERE nome = 'Legumes e fruta'),       'kg',  4.00,  6.00,  2.10),
    ('Lombo de salmão',   (SELECT id FROM categorias WHERE nome = 'Peixe e marisco'),       'kg',  3.00,  2.00, 14.50),
    ('Massa spaghetti',   (SELECT id FROM categorias WHERE nome = 'Massas e farinhas'),     'kg',  5.00,  3.00,  1.60),
    ('Sal',               (SELECT id FROM categorias WHERE nome = 'Ervas e especiarias'),   'kg',  3.00,  1.00,  0.40);

INSERT INTO receitas (titulo, descricao, porcoes, tempo_preparacao_min, instrucoes) VALUES
    ('Massa ao alho e azeite',
     'Clássico rápido para o serviço do almoço.',
     4, 20,
     'Cozer a massa em água com sal. Dourar o alho no azeite sem queimar. Juntar a massa e envolver bem.'),
    ('Crepes simples',
     'Base de crepes para doce ou salgado.',
     6, 30,
     'Misturar farinha, ovos e leite. Deixar repousar 15 minutos. Cozinhar em frigideira com manteiga.');

INSERT INTO receita_ingredientes (receita_id, ingrediente_id, quantidade) VALUES
    ((SELECT id FROM receitas WHERE titulo = 'Massa ao alho e azeite'), (SELECT id FROM ingredientes WHERE nome = 'Massa spaghetti'),    0.40),
    ((SELECT id FROM receitas WHERE titulo = 'Massa ao alho e azeite'), (SELECT id FROM ingredientes WHERE nome = 'Alho'),               0.03),
    ((SELECT id FROM receitas WHERE titulo = 'Massa ao alho e azeite'), (SELECT id FROM ingredientes WHERE nome = 'Azeite virgem extra'), 0.10),
    ((SELECT id FROM receitas WHERE titulo = 'Massa ao alho e azeite'), (SELECT id FROM ingredientes WHERE nome = 'Sal'),                0.01),
    ((SELECT id FROM receitas WHERE titulo = 'Crepes simples'),         (SELECT id FROM ingredientes WHERE nome = 'Farinha de trigo'),  0.25),
    ((SELECT id FROM receitas WHERE titulo = 'Crepes simples'),         (SELECT id FROM ingredientes WHERE nome = 'Ovos'),              3.00),
    ((SELECT id FROM receitas WHERE titulo = 'Crepes simples'),         (SELECT id FROM ingredientes WHERE nome = 'Leite'),             0.50),
    ((SELECT id FROM receitas WHERE titulo = 'Crepes simples'),         (SELECT id FROM ingredientes WHERE nome = 'Manteiga'),          0.05);
