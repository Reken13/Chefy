<?php
/*
 * Receitas — APAGAR. As linhas de receita_ingredientes apagam-se sozinhas
 * (ON DELETE CASCADE na base de dados).
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();
exigir_post();
validar_csrf();

$id = (int) ($_POST['id'] ?? 0);

if (db_executar('DELETE FROM receitas WHERE id = :id', [':id' => $id]) > 0) {
    definir_flash('success', 'Receita apagada.');
} else {
    definir_flash('danger', 'Essa receita não existe.');
}

redirecionar('modulos/receitas/index.php');
