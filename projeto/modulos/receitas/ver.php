<?php
/*
 * Receitas — VER o detalhe: ingredientes, custo estimado e se há stock suficiente.
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();

$id = (int) ($_GET['id'] ?? 0);

$receita = db_um('SELECT * FROM receitas WHERE id = :id', [':id' => $id]);
if (!$receita) {
    definir_flash('danger', 'Essa receita não existe.');
    redirecionar('modulos/receitas/index.php');
}

// JOIN: junta a tabela de ligação com os dados de cada ingrediente.
$linhas = db_todos(
    'SELECT i.nome, i.unidade, i.stock_atual, i.custo_unitario, ri.quantidade
       FROM receita_ingredientes ri
       JOIN ingredientes i ON i.id = ri.ingrediente_id
      WHERE ri.receita_id = :id
      ORDER BY i.nome',
    [':id' => $id]
);

// Custo total = soma de (quantidade × custo unitário).
$custo_total = 0.0;
foreach ($linhas as $l) {
    $custo_total += $l['quantidade'] * $l['custo_unitario'];
}
$custo_porcao = $receita['porcoes'] > 0 ? $custo_total / $receita['porcoes'] : 0;

$titulo_pagina = $receita['titulo'];
$pagina_ativa  = 'receitas';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-3">
    <div>
        <h1 class="mb-1"><?= e($receita['titulo']) ?></h1>
        <p class="text-muted mb-0"><?= (int) $receita['tempo_preparacao_min'] ?> min · <?= (int) $receita['porcoes'] ?> porções</p>
    </div>
    <div class="d-flex gap-2">
        <a class="btn btn-outline-primary" href="<?= e(url('modulos/receitas/index.php')) ?>">← Voltar</a>
        <a class="btn btn-primary" href="<?= e(url('modulos/receitas/form.php?id=' . $id)) ?>">Editar</a>
    </div>
</div>

<?php if ($receita['descricao']): ?>
    <p class="lead"><?= e($receita['descricao']) ?></p>
<?php endif; ?>

<div class="row g-3">
    <div class="col-lg-7">
        <div class="card h-100">
            <div class="card-header">Ingredientes</div>
            <div class="table-responsive">
                <table class="table mb-0">
                    <thead>
                        <tr><th>Ingrediente</th><th class="text-end">Quantidade</th><th class="text-end">Stock</th></tr>
                    </thead>
                    <tbody>
                    <?php foreach ($linhas as $l): ?>
                        <?php $falta = $l['stock_atual'] < $l['quantidade']; ?>
                        <tr>
                            <td><?= e($l['nome']) ?></td>
                            <td class="text-end"><?= e(formatar_numero($l['quantidade'])) ?> <?= e($l['unidade']) ?></td>
                            <td class="text-end">
                                <?= e(formatar_numero($l['stock_atual'])) ?> <?= e($l['unidade']) ?>
                                <?php if ($falta): ?><span class="selo-baixo ms-1">insuficiente</span><?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="col-lg-5">
        <div class="card mb-3">
            <div class="card-body">
                <div class="estatistica"><?= e(formatar_euro($custo_total)) ?></div>
                <div class="estatistica-etiqueta">Custo estimado da receita</div>
                <hr>
                <div class="fw-bold"><?= e(formatar_euro($custo_porcao)) ?> <span class="text-muted fw-normal">por porção</span></div>
            </div>
        </div>
        <div class="card">
            <div class="card-header">Preparação</div>
            <div class="card-body">
                <?php if (trim((string) $receita['instrucoes']) === ''): ?>
                    <span class="text-muted">Sem instruções.</span>
                <?php else: ?>
                    <?= nl2br(e($receita['instrucoes'])) ?>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
