<?php
/*
 * Receitas — LISTAR + PESQUISAR.
 * A pesquisa ?q=texto procura no título da receita OU no nome dos seus ingredientes.
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();

$q = trim($_GET['q'] ?? '');

$sql = 'SELECT r.id, r.titulo, r.descricao, r.porcoes, r.tempo_preparacao_min,
               (SELECT COUNT(*) FROM receita_ingredientes ri WHERE ri.receita_id = r.id) AS n_ingredientes
          FROM receitas r
         WHERE 1 = 1';
$parametros = [];

if ($q !== '') {
    // Atenção: com prepared statements reais, cada marcador só pode aparecer UMA vez.
    // Por isso usamos :q1 e :q2 com o mesmo valor.
    $sql .= ' AND (r.titulo LIKE :q1
                   OR EXISTS (SELECT 1
                                FROM receita_ingredientes ri
                                JOIN ingredientes i ON i.id = ri.ingrediente_id
                               WHERE ri.receita_id = r.id AND i.nome LIKE :q2))';
    $parametros[':q1'] = like_seguro($q);
    $parametros[':q2'] = like_seguro($q);
}
$sql .= ' ORDER BY r.titulo';

$receitas = db_todos($sql, $parametros);

$titulo_pagina = 'Receitas';
$pagina_ativa  = 'receitas';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
    <h1 class="mb-0">Receitas</h1>
    <a class="btn btn-primary" href="<?= e(url('modulos/receitas/form.php')) ?>">+ Nova receita</a>
</div>

<form method="get" class="card card-body mb-3">
    <div class="row g-2 align-items-end">
        <div class="col-md-9">
            <label class="form-label" for="q">Pesquisar</label>
            <input class="form-control" type="search" id="q" name="q" value="<?= e($q) ?>"
                   placeholder="Título da receita ou ingrediente">
        </div>
        <div class="col-md-3 d-flex gap-2">
            <button class="btn btn-primary flex-grow-1" type="submit">Pesquisar</button>
            <?php if ($q !== ''): ?>
                <a class="btn btn-outline-primary" href="<?= e(url('modulos/receitas/index.php')) ?>" title="Limpar">✕</a>
            <?php endif; ?>
        </div>
    </div>
</form>

<?php if (!$receitas): ?>
    <div class="card">
        <div class="estado-vazio">
            <img src="<?= e(url('assets/img/logo.svg')) ?>" alt="" width="56" height="56"><br>
            <?= $q !== '' ? 'Nenhuma receita corresponde à pesquisa.' : 'Ainda não tens receitas. Vamos começar?' ?>
        </div>
    </div>
<?php else: ?>
    <div class="row g-3">
        <?php foreach ($receitas as $r): ?>
            <div class="col-md-6 col-lg-4">
                <div class="card h-100">
                    <div class="card-body d-flex flex-column">
                        <h2 class="h4">
                            <a class="text-decoration-none" href="<?= e(url('modulos/receitas/ver.php?id=' . (int) $r['id'])) ?>">
                                <?= e($r['titulo']) ?>
                            </a>
                        </h2>
                        <p class="text-muted small mb-2">
                            <?= (int) $r['tempo_preparacao_min'] ?> min · <?= (int) $r['porcoes'] ?> porções ·
                            <?= (int) $r['n_ingredientes'] ?> ingredientes
                        </p>
                        <p class="flex-grow-1"><?= e($r['descricao']) ?></p>
                        <div class="d-flex gap-2">
                            <a class="btn btn-sm btn-primary" href="<?= e(url('modulos/receitas/ver.php?id=' . (int) $r['id'])) ?>">Ver</a>
                            <a class="btn btn-sm btn-outline-primary" href="<?= e(url('modulos/receitas/form.php?id=' . (int) $r['id'])) ?>">Editar</a>
                            <form method="post" action="<?= e(url('modulos/receitas/apagar.php')) ?>"
                                  data-confirmar="Apagar a receita «<?= e($r['titulo']) ?>»?">
                                <?= campo_csrf() ?>
                                <input type="hidden" name="id" value="<?= (int) $r['id'] ?>">
                                <button class="btn btn-sm btn-outline-danger" type="submit">Apagar</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
<?php endif; ?>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
