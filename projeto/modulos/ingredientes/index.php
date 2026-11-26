<?php
/*
 * Ingredientes — LISTAR + PESQUISAR  (o "R" do CRUD: Read).
 * Filtros por GET (ficam no URL, por isso a pesquisa pode ser partilhada/guardada):
 *   ?q=texto  ?categoria=3  ?baixo=1
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();

$q         = trim($_GET['q'] ?? '');
$categoria = (int) ($_GET['categoria'] ?? 0);
$so_baixo  = !empty($_GET['baixo']);

// Construímos o SQL por partes. Cada filtro acrescenta uma condição e o seu valor.
// Os VALORES vão sempre em $parametros (nunca dentro do texto do SQL).
$sql = 'SELECT i.id, i.nome, i.unidade, i.stock_atual, i.stock_minimo, i.custo_unitario,
               c.nome AS categoria
          FROM ingredientes i
          JOIN categorias c ON c.id = i.categoria_id
         WHERE 1 = 1';
$parametros = [];

if ($q !== '') {
    $sql .= ' AND i.nome LIKE :q';
    $parametros[':q'] = like_seguro($q);
}
if ($categoria > 0) {
    $sql .= ' AND i.categoria_id = :categoria';
    $parametros[':categoria'] = $categoria;
}
if ($so_baixo) {
    $sql .= ' AND ' . SQL_STOCK_BAIXO;
}
$sql .= ' ORDER BY i.nome';

$ingredientes = db_todos($sql, $parametros);
$categorias   = db_todos('SELECT id, nome FROM categorias ORDER BY nome');
$ha_filtros   = ($q !== '' || $categoria > 0 || $so_baixo);

$titulo_pagina = 'Ingredientes';
$pagina_ativa  = 'ingredientes';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
    <h1 class="mb-0">Ingredientes</h1>
    <a class="btn btn-primary" href="<?= e(url('modulos/ingredientes/form.php')) ?>">+ Novo ingrediente</a>
</div>

<form method="get" class="card card-body mb-3">
    <div class="row g-2 align-items-end">
        <div class="col-md-5">
            <label class="form-label" for="q">Pesquisar</label>
            <input class="form-control" type="search" id="q" name="q" value="<?= e($q) ?>" placeholder="Nome do ingrediente">
        </div>
        <div class="col-md-3">
            <label class="form-label" for="categoria">Categoria</label>
            <select class="form-select" id="categoria" name="categoria" data-auto-enviar>
                <option value="0">Todas</option>
                <?php foreach ($categorias as $c): ?>
                    <option value="<?= (int) $c['id'] ?>" <?= $categoria === (int) $c['id'] ? 'selected' : '' ?>><?= e($c['nome']) ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="col-md-2">
            <div class="form-check mb-2">
                <input class="form-check-input" type="checkbox" id="baixo" name="baixo" value="1"
                       <?= $so_baixo ? 'checked' : '' ?> data-auto-enviar>
                <label class="form-check-label" for="baixo">Só stock baixo</label>
            </div>
        </div>
        <div class="col-md-2 d-flex gap-2">
            <button class="btn btn-primary flex-grow-1" type="submit">Pesquisar</button>
            <?php if ($ha_filtros): ?>
                <a class="btn btn-outline-primary" href="<?= e(url('modulos/ingredientes/index.php')) ?>" title="Limpar filtros">✕</a>
            <?php endif; ?>
        </div>
    </div>
</form>

<div class="card">
    <?php if (!$ingredientes): ?>
        <div class="estado-vazio">
            <img src="<?= e(url('assets/img/logo.svg')) ?>" alt="" width="56" height="56"><br>
            <?= $ha_filtros ? 'Nenhum ingrediente corresponde à pesquisa.' : 'Ainda não tens ingredientes. Vamos começar?' ?>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Categoria</th>
                        <th class="text-end">Stock</th>
                        <th class="text-end">Custo</th>
                        <th class="text-end">Ações</th>
                    </tr>
                </thead>
                <tbody>
                <?php foreach ($ingredientes as $ing): ?>
                    <?php $baixo = $ing['stock_minimo'] > 0 && $ing['stock_atual'] <= $ing['stock_minimo']; ?>
                    <tr>
                        <td class="fw-bold"><?= e($ing['nome']) ?></td>
                        <td><?= e($ing['categoria']) ?></td>
                        <td class="text-end">
                            <?= e(formatar_numero($ing['stock_atual'])) ?> <?= e($ing['unidade']) ?>
                            <?php if ($baixo): ?><span class="selo-baixo ms-1">baixo</span><?php endif; ?>
                        </td>
                        <td class="text-end"><?= e(formatar_euro($ing['custo_unitario'])) ?>/<?= e($ing['unidade']) ?></td>
                        <td class="text-end">
                            <div class="d-inline-flex gap-2">
                                <a class="btn btn-sm btn-outline-primary"
                                   href="<?= e(url('modulos/ingredientes/form.php?id=' . (int) $ing['id'])) ?>">Editar</a>
                                <form method="post" action="<?= e(url('modulos/ingredientes/apagar.php')) ?>"
                                      data-confirmar="Apagar «<?= e($ing['nome']) ?>»? Esta ação não pode ser desfeita.">
                                    <?= campo_csrf() ?>
                                    <input type="hidden" name="id" value="<?= (int) $ing['id'] ?>">
                                    <button class="btn btn-sm btn-outline-danger" type="submit">Apagar</button>
                                </form>
                            </div>
                        </td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <div class="card-footer bg-white small text-muted"><?= count($ingredientes) ?> ingrediente(s)</div>
    <?php endif; ?>
</div>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
