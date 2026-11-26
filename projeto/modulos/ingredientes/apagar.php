<?php
/*
 * Ingredientes — APAGAR (o "D" do CRUD). Só aceita POST + token CSRF.
 */
require __DIR__ . '/../../includes/inicio.php';
exigir_login();
exigir_post();
validar_csrf();

$id = (int) ($_POST['id'] ?? 0);

try {
    $apagados = db_executar('DELETE FROM ingredientes WHERE id = :id', [':id' => $id]);
    if ($apagados > 0) {
        definir_flash('success', 'Ingrediente apagado.');
    } else {
        definir_flash('danger', 'Esse ingrediente não existe.');
    }
} catch (PDOException $erro) {
    // 23000 = violação de chave estrangeira: o ingrediente é usado em receitas
    // (a BD protege-nos com ON DELETE RESTRICT).
    if ($erro->getCode() === '23000') {
        definir_flash('danger', 'Não é possível apagar: este ingrediente é usado em receitas.');
    } else {
        throw $erro;
    }
}

redirecionar('modulos/ingredientes/index.php');
