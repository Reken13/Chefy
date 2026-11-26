<?php
/*
 * Painel: resumo da cozinha (totais, ingredientes com stock baixo, últimas receitas).
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();

$total_ingredientes = db_um('SELECT COUNT(*) AS n FROM ingredientes')['n'];
$total_receitas     = db_um('SELECT COUNT(*) AS n FROM receitas')['n'];

$stock_baixo = db_todos(
    'SELECT i.id, i.nome, i.stock_atual, i.stock_minimo, i.unidade
       FROM ingredientes i
      WHERE ' . SQL_STOCK_BAIXO . '
      ORDER BY i.nome'
);

$ultimas_receitas = db_todos(
    'SELECT id, titulo, tempo_preparacao_min, porcoes
       FROM receitas
      ORDER BY criado_em DESC, id DESC
      LIMIT 5'
);

$titulo_pagina = 'Painel';
$pagina_ativa  = 'painel';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<h1 class="mb-1">Olá, <?= e(utilizador_atual()['nome']) ?></h1>
<p class="text-muted mb-4">Tudo no seu lugar. Tudo pronto para o serviço.</p>

<div class="row g-3 mb-4">
    <div class="col-6 col-md-4">
        <a class="text-decoration-none" href="<?= e(url('modulos/ingredientes/index.php')) ?>">
            <div class="card h-100"><div class="card-body">
                <div class="estatistica"><?= (int) $total_ingredientes ?></div>
                <div class="estatistica-etiqueta">Ingredientes</div>
            </div></div>
        </a>
    </div>
    <div class="col-6 col-md-4">
        <a class="text-decoration-none" href="<?= e(url('modulos/receitas/index.php')) ?>">
            <div class="card h-100"><div class="card-body">
                <div class="estatistica"><?= (int) $total_receitas ?></div>
                <div class="estatistica-etiqueta">Receitas</div>
            </div></div>
        </a>
    </div>
    <div class="col-12 col-md-4">
        <a class="text-decoration-none" href="<?= e(url('modulos/ingredientes/index.php?baixo=1')) ?>">
            <div class="card h-100"><div class="card-body">
                <div class="estatistica <?= $stock_baixo ? 'alerta' : '' ?>"><?= count($stock_baixo) ?></div>
                <div class="estatistica-etiqueta">Com stock baixo</div>
            </div></div>
        </a>
    </div>
</div>

<div class="row g-3">
    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header">Stock baixo</div>
            <?php if (!$stock_baixo): ?>
                <div class="estado-vazio">Todo o inventário está em ordem.</div>
            <?php else: ?>
                <ul class="list-group list-group-flush">
                    <?php foreach ($stock_baixo as $ing): ?>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="<?= e(url('modulos/ingredientes/form.php?id=' . (int) $ing['id'])) ?>"><?= e($ing['nome']) ?></a>
                            <span class="selo-baixo">
                                <?= e(formatar_numero($ing['stock_atual'])) ?> / mín. <?= e(formatar_numero($ing['stock_minimo'])) ?> <?= e($ing['unidade']) ?>
                            </span>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header">Últimas receitas</div>
            <?php if (!$ultimas_receitas): ?>
                <div class="estado-vazio">
                    <img src="<?= e(url('assets/img/logo.svg')) ?>" alt="" width="56" height="56"><br>
                    Ainda não tens receitas. Vamos começar?<br>
                    <a class="btn btn-primary mt-3" href="<?= e(url('modulos/receitas/form.php')) ?>">Nova receita</a>
                </div>
            <?php else: ?>
                <ul class="list-group list-group-flush">
                    <?php foreach ($ultimas_receitas as $r): ?>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <a href="<?= e(url('modulos/receitas/ver.php?id=' . (int) $r['id'])) ?>"><?= e($r['titulo']) ?></a>
                            <span class="text-muted small"><?= (int) $r['tempo_preparacao_min'] ?> min · <?= (int) $r['porcoes'] ?> porções</span>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </div>
    </div>
</div>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
