<?php
/*
 * cabecalho.php — parte de cima comum a todas as páginas (head + menu + mensagens).
 * Antes de o incluir, a página define:
 *   $titulo_pagina  -> texto do separador do browser
 *   $pagina_ativa   -> 'painel' | 'ingredientes' | 'receitas'  (para destacar o menu)
 */
$titulo_pagina = $titulo_pagina ?? 'Chefy';
$pagina_ativa  = $pagina_ativa ?? '';
$utilizador    = utilizador_atual();

/** Escreve "active" se o link for o da página atual. */
function ativo(string $nome, string $pagina_ativa): string
{
    return $nome === $pagina_ativa ? 'active' : '';
}
?>
<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= e($titulo_pagina) ?> · Chefy</title>
    <link rel="icon" type="image/svg+xml" href="<?= e(url('assets/img/logo.svg')) ?>">

    <!-- Fontes da marca: Lilita One (títulos) e Nunito (texto) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lilita+One&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">

    <!-- Bootstrap 5 (CSS) e o nosso CSS por cima -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="<?= e(url('assets/css/chefy.css')) ?>" rel="stylesheet">
</head>
<body>

<nav class="navbar navbar-expand-md chefy-navbar">
    <div class="container">
        <a class="navbar-brand d-flex align-items-center gap-2"
           href="<?= e(url($utilizador ? 'modulos/painel/index.php' : 'modulos/auth/login.php')) ?>">
            <img src="<?= e(url('assets/img/logo.svg')) ?>" alt="" width="36" height="36">
            <span class="chefy-wordmark">chefy</span>
        </a>

        <?php if ($utilizador): ?>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                    data-bs-target="#menu" aria-controls="menu" aria-expanded="false" aria-label="Abrir menu">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="menu">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link <?= ativo('painel', $pagina_ativa) ?>"
                           href="<?= e(url('modulos/painel/index.php')) ?>">Painel</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= ativo('ingredientes', $pagina_ativa) ?>"
                           href="<?= e(url('modulos/ingredientes/index.php')) ?>">Ingredientes</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= ativo('receitas', $pagina_ativa) ?>"
                           href="<?= e(url('modulos/receitas/index.php')) ?>">Receitas</a>
                    </li>
                </ul>

                <form method="post" action="<?= e(url('modulos/auth/logout.php')) ?>"
                      class="d-flex align-items-center gap-3">
                    <?= campo_csrf() ?>
                    <span class="small text-muted"><?= e($utilizador['nome']) ?></span>
                    <button type="submit" class="btn btn-sm btn-outline-primary">Terminar sessão</button>
                </form>
            </div>
        <?php endif; ?>
    </div>
</nav>

<main class="container py-4">
    <?php foreach (obter_flashes() as $flash): ?>
        <div class="alert alert-<?= e($flash['tipo']) ?> alert-dismissible fade show" role="alert">
            <?= e($flash['mensagem']) ?>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        </div>
    <?php endforeach; ?>
