<?php
/*
 * Ingredientes — CRIAR e EDITAR (o "C" e o "U" do CRUD), no mesmo ficheiro.
 *   form.php         -> formulário vazio  = CRIAR
 *   form.php?id=5    -> formulário cheio  = EDITAR o ingrediente 5
 *
 * Fluxo: GET mostra o formulário; POST valida e grava; se houver erros,
 * mostra o formulário outra vez com os erros e com o que o utilizador escreveu.
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();

$id = (int) ($_GET['id'] ?? $_POST['id'] ?? 0);

// Valores iniciais do formulário (criar).
$ingrediente = [
    'nome' => '', 'categoria_id' => 0, 'unidade' => 'kg',
    'stock_atual' => '0', 'stock_minimo' => '0', 'custo_unitario' => '0',
];

// Se há id, vamos buscar o ingrediente à BD (editar).
if ($id > 0) {
    $existente = db_um('SELECT * FROM ingredientes WHERE id = :id', [':id' => $id]);
    if (!$existente) {
        definir_flash('danger', 'Esse ingrediente não existe.');
        redirecionar('modulos/ingredientes/index.php');
    }
    $ingrediente = $existente;
}

$categorias = db_todos('SELECT id, nome FROM categorias ORDER BY nome');
$erros = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    validar_csrf();

    // Lemos o que veio do formulário...
    $ingrediente = [
        'nome'           => trim($_POST['nome'] ?? ''),
        'categoria_id'   => (int) ($_POST['categoria_id'] ?? 0),
        'unidade'        => $_POST['unidade'] ?? '',
        'stock_atual'    => trim($_POST['stock_atual'] ?? ''),
        'stock_minimo'   => trim($_POST['stock_minimo'] ?? ''),
        'custo_unitario' => trim($_POST['custo_unitario'] ?? ''),
    ];

    // ...e validamos tudo no servidor.
    if ($ingrediente['nome'] === '' || mb_strlen($ingrediente['nome']) > 100) {
        $erros['nome'] = 'Indica o nome (máximo 100 letras).';
    } elseif (db_um('SELECT id FROM ingredientes WHERE nome = :nome AND id <> :id',
                    [':nome' => $ingrediente['nome'], ':id' => $id])) {
        $erros['nome'] = 'Já existe um ingrediente com este nome.';
    }

    if (!in_array($ingrediente['categoria_id'], array_map('intval', array_column($categorias, 'id')), true)) {
        $erros['categoria_id'] = 'Escolhe uma categoria.';
    }
    if (!in_array($ingrediente['unidade'], UNIDADES, true)) {
        $erros['unidade'] = 'Escolhe uma unidade.';
    }

    // Os 3 números: têm de ser números e não negativos.
    $numeros = [];
    foreach (['stock_atual', 'stock_minimo', 'custo_unitario'] as $campo) {
        $valor = para_decimal($ingrediente[$campo]);
        if ($valor === null || $valor < 0 || $valor > 99999999) {
            $erros[$campo] = 'Indica um número maior ou igual a 0.';
        }
        $numeros[$campo] = $valor;
    }

    // Sem erros -> gravar.
    if (!$erros) {
        $parametros = [
            ':nome'      => $ingrediente['nome'],
            ':categoria' => $ingrediente['categoria_id'],
            ':unidade'   => $ingrediente['unidade'],
            ':atual'     => $numeros['stock_atual'],
            ':minimo'    => $numeros['stock_minimo'],
            ':custo'     => $numeros['custo_unitario'],
        ];

        if ($id > 0) {
            $parametros[':id'] = $id;
            db_executar(
                'UPDATE ingredientes
                    SET nome = :nome, categoria_id = :categoria, unidade = :unidade,
                        stock_atual = :atual, stock_minimo = :minimo, custo_unitario = :custo
                  WHERE id = :id',
                $parametros
            );
            definir_flash('success', 'Ingrediente atualizado com sucesso!');
        } else {
            $parametros[':criado_por'] = utilizador_atual()['id'];
            db_executar(
                'INSERT INTO ingredientes (nome, categoria_id, unidade, stock_atual, stock_minimo, custo_unitario, criado_por)
                 VALUES (:nome, :categoria, :unidade, :atual, :minimo, :custo, :criado_por)',
                $parametros
            );
            definir_flash('success', 'Ingrediente guardado com sucesso!');
        }
        redirecionar('modulos/ingredientes/index.php'); // evita reenviar o POST ao recarregar (F5)
    }
}

$titulo_pagina = $id > 0 ? 'Editar ingrediente' : 'Novo ingrediente';
$pagina_ativa  = 'ingredientes';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<h1 class="mb-3"><?= e($titulo_pagina) ?></h1>

<div class="card" style="max-width: 720px;">
    <div class="card-body p-4">
        <form method="post" novalidate>
            <?= campo_csrf() ?>
            <input type="hidden" name="id" value="<?= (int) $id ?>">

            <div class="mb-3">
                <label class="form-label" for="nome">Nome</label>
                <input class="form-control<?= invalido($erros, 'nome') ?>" type="text" id="nome" name="nome"
                       maxlength="100" value="<?= e($ingrediente['nome']) ?>" required autofocus>
                <div class="invalid-feedback"><?= e($erros['nome'] ?? '') ?></div>
            </div>

            <div class="row g-3 mb-3">
                <div class="col-md-8">
                    <label class="form-label" for="categoria_id">Categoria</label>
                    <select class="form-select<?= invalido($erros, 'categoria_id') ?>" id="categoria_id" name="categoria_id" required>
                        <option value="">— escolher —</option>
                        <?php foreach ($categorias as $c): ?>
                            <option value="<?= (int) $c['id'] ?>" <?= (int) $ingrediente['categoria_id'] === (int) $c['id'] ? 'selected' : '' ?>>
                                <?= e($c['nome']) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <div class="invalid-feedback"><?= e($erros['categoria_id'] ?? '') ?></div>
                </div>
                <div class="col-md-4">
                    <label class="form-label" for="unidade">Unidade</label>
                    <select class="form-select<?= invalido($erros, 'unidade') ?>" id="unidade" name="unidade" required>
                        <?php foreach (UNIDADES as $u): ?>
                            <option value="<?= e($u) ?>" <?= $ingrediente['unidade'] === $u ? 'selected' : '' ?>><?= e($u) ?></option>
                        <?php endforeach; ?>
                    </select>
                    <div class="invalid-feedback"><?= e($erros['unidade'] ?? '') ?></div>
                </div>
            </div>

            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <label class="form-label" for="stock_atual">Stock atual</label>
                    <input class="form-control<?= invalido($erros, 'stock_atual') ?>" type="text" inputmode="decimal"
                           id="stock_atual" name="stock_atual" value="<?= e($ingrediente['stock_atual']) ?>" required>
                    <div class="invalid-feedback"><?= e($erros['stock_atual'] ?? '') ?></div>
                </div>
                <div class="col-md-4">
                    <label class="form-label" for="stock_minimo">Stock mínimo</label>
                    <input class="form-control<?= invalido($erros, 'stock_minimo') ?>" type="text" inputmode="decimal"
                           id="stock_minimo" name="stock_minimo" value="<?= e($ingrediente['stock_minimo']) ?>" required>
                    <div class="form-text">Abaixo disto aparece como «stock baixo».</div>
                    <div class="invalid-feedback"><?= e($erros['stock_minimo'] ?? '') ?></div>
                </div>
                <div class="col-md-4">
                    <label class="form-label" for="custo_unitario">Custo por unidade (€)</label>
                    <input class="form-control<?= invalido($erros, 'custo_unitario') ?>" type="text" inputmode="decimal"
                           id="custo_unitario" name="custo_unitario" value="<?= e($ingrediente['custo_unitario']) ?>" required>
                    <div class="invalid-feedback"><?= e($erros['custo_unitario'] ?? '') ?></div>
                </div>
            </div>

            <div class="d-flex gap-2">
                <button class="btn btn-primary" type="submit">Guardar</button>
                <a class="btn btn-outline-primary" href="<?= e(url('modulos/ingredientes/index.php')) ?>">Cancelar</a>
            </div>
        </form>
    </div>
</div>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
