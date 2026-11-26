# Chefy

Aplicação web modular em **PHP + MySQL/MariaDB** para gestão de cozinha profissional, do ponto de vista do chef.
Projeto de Programação Ambiente Web (UA) — grupo G16.

**Menos caos. Mais cozinha.**

## Funcionalidades (1.ª entrega)

- **Registo e login** de utilizadores com sessões seguras.
- **Ingredientes** (inventário): criar, listar, pesquisar (nome, categoria, stock baixo), editar e apagar.
- **Receitas**: criar, listar, pesquisar (título ou ingrediente), ver (custo estimado e stock disponível), editar e apagar.
- **Painel** com totais, ingredientes com stock baixo e últimas receitas.

## Tecnologias

PHP (PDO). Testado com PHP 8.3; escrito para ser compatível com 7.4+ (por confirmar na versão do servidor) · MySQL/MariaDB · HTML5 · CSS (Bootstrap 5 + CSS próprio com a identidade Chefy) · JavaScript (jQuery 3).
Sem frameworks de servidor.

## Estrutura

```
index.php            ponto de entrada
config/              configuração (config.php não vai para o Git)
includes/            código partilhado (arranque, BD, sessão, funções, cabeçalho/rodapé)
modulos/             páginas por módulo: auth, painel, ingredientes, receitas
assets/              css, js, imagens
sql/                 schema.sql e dados_exemplo.sql
docs/                documentação (base de dados)
```

## Instalação

1. Criar uma base de dados (`utf8mb4_unicode_ci`) e importar, por esta ordem, `sql/schema.sql` e `sql/dados_exemplo.sql`.
2. Copiar `config/config.example.php` para `config/config.php` e preencher os dados da BD e o `base_url`.
3. Abrir o `index.php` no browser e criar uma conta em «Criar conta».

Em local, sem Apache: `php -S localhost:8000` (dentro da pasta `projeto`).

## Documentação

- [Base de dados: diagrama e explicação](docs/BASE_DE_DADOS.md)

## Segurança (resumo)

Consultas preparadas (PDO) · passwords com `password_hash` · tokens CSRF em todos os formulários · escape de saída (XSS) ·
`session_regenerate_id` no login · cookie de sessão `HttpOnly`/`SameSite` com nome próprio · expiração por inatividade · validação no servidor.
