<?php
/*
 * Receitas — CRIAR e EDITAR.
 * Particularidade: uma receita tem VÁRIOS ingredientes (relação N:M). O formulário
 * envia duas listas paralelas:  ing_id[]  e  ing_qtd[]  (a posição 0 de uma
 * corresponde à posição 0 da outra). O jQuery (assets/js/chefy.js) acrescenta linhas.
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();

$id = (int) ($_GET['id'] ?? $_POST['id'] ?? 0);

$receita = [
    'titulo' => '', 'descricao' => '', 'porcoes' => '4',
    'tempo_preparacao_min' => '30', 'instrucoes' => '',
];
$linhas = []; // cada linha: ['ingrediente_id' => .., 'quantidade' => ..]

if ($id > 0) {
    $existente = db_um('SELECT * FROM receitas WHERE id = :id', [':id' => $id]);
    if (!$existente) {
        definir_flash('danger', 'Essa receita não existe.');
        redirecionar('modulos/receitas/index.php');
    }
    $receita = $existente;
    $linhas  = db_todos(
        'SELECT ingrediente_id, quantidade FROM receita_ingredientes WHERE receita_id = :id',
        [':id' => $id]
    );
}

$ingredientes = db_todos(
    'SELECT id, nome, unidade FROM ingredientes ORDER BY nome'
);
$ids_validos = array_map('intval', array_column($ingredientes, 'id'));
$erros = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    validar_csrf();

    $receita = [
        'titulo'               => trim($_POST['titulo'] ?? ''),
        'descricao'            => trim($_POST['descricao'] ?? ''),
        'porcoes'              => trim($_POST['porcoes'] ?? ''),
        'tempo_preparacao_min' => trim($_POST['tempo_preparacao_min'] ?? ''),
        'instrucoes'           => trim($_POST['instrucoes'] ?? ''),
    ];

    if ($receita['titulo'] === '' || mb_strlen($receita['titulo']) > 150) {
        $erros['titulo'] = 'Indica o título (máximo 150 letras).';
    }
    if (mb_strlen($receita['descricao']) > 500) {
        $erros['descricao'] = 'A descrição pode ter no máximo 500 letras.';
    }
    $porcoes = filter_var($receita['porcoes'], FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 1000]]);
    if ($porcoes === false) {
        $erros['porcoes'] = 'Indica um número de porções entre 1 e 1000.';
    }
    $tempo = filter_var($receita['tempo_preparacao_min'], FILTER_VALIDATE_INT, ['options' => ['min_range' => 0, 'max_range' => 10000]]);
    if ($tempo === false) {
        $erros['tempo_preparacao_min'] = 'Indica o tempo em minutos (0 ou mais).';
    }

    // --- Linhas de ingredientes ---
    $linhas = [];
    $vistos = [];
    $ids_post = $_POST['ing_id'] ?? [];
    $qtd_post = $_POST['ing_qtd'] ?? [];
    if (!is_array($ids_post) || !is_array($qtd_post)) {
        $ids_post = $qtd_post = [];
    }

    foreach ($ids_post as $i => $ing_id) {
        $ing_id = (int) $ing_id;
        $qtd_texto = trim((string) ($qtd_post[$i] ?? ''));

        if ($ing_id === 0 && $qtd_texto === '') {
            continue; // linha vazia: ignorar
        }
        $linhas[] = ['ingrediente_id' => $ing_id, 'quantidade' => $qtd_texto];

        $qtd = para_decimal($qtd_texto);
        if (!in_array($ing_id, $ids_validos, true)) {
            $erros['ingredientes'] = 'Escolhe um ingrediente em todas as linhas preenchidas.';
        } elseif ($qtd === null || $qtd <= 0 || $qtd > 99999999) {
            $erros['ingredientes'] = 'Indica uma quantidade maior que 0 em cada ingrediente.';
        } elseif (isset($vistos[$ing_id])) {
            $erros['ingredientes'] = 'Um ingrediente não pode aparecer duas vezes na mesma receita.';
        }
        $vistos[$ing_id] = true;
    }
    if (!$linhas && !isset($erros['ingredientes'])) {
        $erros['ingredientes'] = 'Adiciona pelo menos um ingrediente.';
    }

    // --- Gravar (TRANSAÇÃO: ou fica tudo gravado, ou nada) ---
    if (!$erros) {
        $pdo = db();
        $pdo->beginTransaction();
        try {
            $dados = [
                ':titulo'     => $receita['titulo'],
                ':descricao'  => $receita['descricao'] === '' ? null : $receita['descricao'],
                ':porcoes'    => $porcoes,
                ':tempo'      => $tempo,
                ':instrucoes' => $receita['instrucoes'] === '' ? null : $receita['instrucoes'],
            ];

            if ($id > 0) {
                $dados[':id'] = $id;
                db_executar(
                    'UPDATE receitas
                        SET titulo = :titulo, descricao = :descricao, porcoes = :porcoes,
                            tempo_preparacao_min = :tempo, instrucoes = :instrucoes
                      WHERE id = :id',
                    $dados
                );
                // Mais simples: apagar as linhas antigas e inserir as novas.
                db_executar('DELETE FROM receita_ingredientes WHERE receita_id = :id', [':id' => $id]);
            } else {
                $dados[':criado_por'] = utilizador_atual()['id'];
                db_executar(
                    'INSERT INTO receitas (titulo, descricao, porcoes, tempo_preparacao_min, instrucoes, criado_por)
                     VALUES (:titulo, :descricao, :porcoes, :tempo, :instrucoes, :criado_por)',
                    $dados
                );
                $id = db_ultimo_id();
            }

            foreach ($linhas as $l) {
                db_executar(
                    'INSERT INTO receita_ingredientes (receita_id, ingrediente_id, quantidade)
                     VALUES (:receita, :ingrediente, :quantidade)',
                    [
                        ':receita'    => $id,
                        ':ingrediente' => $l['ingrediente_id'],
                        ':quantidade' => para_decimal($l['quantidade']),
                    ]
                );
            }
            $pdo->commit();
        } catch (Throwable $falha) {
            $pdo->rollBack();   // desfaz tudo o que foi feito dentro da transação
            throw $falha;
        }

        definir_flash('success', 'Receita guardada com sucesso!');
        redirecionar('modulos/receitas/ver.php?id=' . $id);
    }
}

if (!$linhas) {
    $linhas = [['ingrediente_id' => 0, 'quantidade' => '']]; // começa com uma linha vazia
}

/** HTML de UMA linha de ingrediente (usada nas linhas existentes e no molde do jQuery). */
function linha_ingrediente(array $ingredientes, $ingrediente_id, $quantidade): string
{
    // Se a quantidade for um número mostramo-la formatada; senão, tal como foi escrita.
    $numero  = para_decimal((string) $quantidade);
    $mostrar = $numero === null ? (string) $quantidade : formatar_numero($numero);
    ob_start(); ?>
    <div class="row g-2 mb-2 linha-ingrediente">
        <div class="col-7 col-md-7">
            <select class="form-select" name="ing_id[]" aria-label="Ingrediente">
                <option value="">— ingrediente —</option>
                <?php foreach ($ingredientes as $ing): ?>
                    <option value="<?= (int) $ing['id'] ?>" <?= (int) $ingrediente_id === (int) $ing['id'] ? 'selected' : '' ?>>
                        <?= e($ing['nome']) ?> (<?= e($ing['unidade']) ?>)
                    </option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="col-3 col-md-3">
            <input class="form-control" type="text" inputmode="decimal" name="ing_qtd[]"
                   value="<?= e($mostrar) ?>"
                   placeholder="Qtd." aria-label="Quantidade">
        </div>
        <div class="col-2 col-md-2">
            <button type="button" class="btn btn-outline-danger w-100 remover-ingrediente" aria-label="Remover linha">✕</button>
        </div>
    </div>
    <?php
    return ob_get_clean();
}

$titulo_pagina = $id > 0 ? 'Editar receita' : 'Nova receita';
$pagina_ativa  = 'receitas';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<h1 class="mb-3"><?= e($titulo_pagina) ?></h1>

<form method="post" novalidate>
    <?= campo_csrf() ?>
    <input type="hidden" name="id" value="<?= (int) $id ?>">

    <div class="row g-3">
        <div class="col-lg-7">
            <div class="card">
                <div class="card-body p-4">
                    <div class="mb-3">
                        <label class="form-label" for="titulo">Título</label>
                        <input class="form-control<?= invalido($erros, 'titulo') ?>" type="text" id="titulo" name="titulo"
                               maxlength="150" value="<?= e($receita['titulo']) ?>" required autofocus>
                        <div class="invalid-feedback"><?= e($erros['titulo'] ?? '') ?></div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label" for="descricao">Descrição (opcional)</label>
                        <input class="form-control<?= invalido($erros, 'descricao') ?>" type="text" id="descricao" name="descricao"
                               maxlength="500" value="<?= e($receita['descricao']) ?>">
                        <div class="invalid-feedback"><?= e($erros['descricao'] ?? '') ?></div>
                    </div>

                    <div class="row g-3 mb-3">
                        <div class="col-6">
                            <label class="form-label" for="porcoes">Porções</label>
                            <input class="form-control<?= invalido($erros, 'porcoes') ?>" type="number" min="1" id="porcoes" name="porcoes"
                                   value="<?= e($receita['porcoes']) ?>" required>
                            <div class="invalid-feedback"><?= e($erros['porcoes'] ?? '') ?></div>
                        </div>
                        <div class="col-6">
                            <label class="form-label" for="tempo_preparacao_min">Tempo (min)</label>
                            <input class="form-control<?= invalido($erros, 'tempo_preparacao_min') ?>" type="number" min="0" id="tempo_preparacao_min"
                                   name="tempo_preparacao_min" value="<?= e($receita['tempo_preparacao_min']) ?>" required>
                            <div class="invalid-feedback"><?= e($erros['tempo_preparacao_min'] ?? '') ?></div>
                        </div>
                    </div>

                    <div class="mb-0">
                        <label class="form-label" for="instrucoes">Preparação</label>
                        <textarea class="form-control" id="instrucoes" name="instrucoes" rows="6"><?= e($receita['instrucoes']) ?></textarea>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-lg-5">
            <div class="card">
                <div class="card-header">Ingredientes</div>
                <div class="card-body">
                    <?php if (!$ingredientes): ?>
                        <div class="alert alert-warning">
                            Ainda não há ingredientes.
                            <a href="<?= e(url('modulos/ingredientes/form.php')) ?>">Cria o primeiro</a> e volta aqui.
                        </div>
                    <?php endif; ?>

                    <?php if (isset($erros['ingredientes'])): ?>
                        <div class="alert alert-danger py-2" role="alert"><?= e($erros['ingredientes']) ?></div>
                    <?php endif; ?>

                    <div id="lista-ingredientes">
                        <?php foreach ($linhas as $l): ?>
                            <?= linha_ingrediente($ingredientes, $l['ingrediente_id'], $l['quantidade']) ?>
                        <?php endforeach; ?>
                    </div>

                    <button type="button" id="adicionar-ingrediente" class="btn btn-outline-primary btn-sm mt-2">
                        + Adicionar ingrediente
                    </button>
                    <div class="form-text">A quantidade usa a unidade do ingrediente (kg, L, un…).</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Molde para o jQuery copiar quando se carrega em "Adicionar ingrediente" -->
    <template id="molde-ingrediente"><?= linha_ingrediente($ingredientes, 0, '') ?></template>

    <div class="d-flex gap-2 mt-4">
        <button class="btn btn-primary" type="submit">Guardar receita</button>
        <a class="btn btn-outline-primary" href="<?= e(url('modulos/receitas/index.php')) ?>">Cancelar</a>
    </div>
</form>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
