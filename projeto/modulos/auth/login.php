<?php
/*
 * Login. Fluxo:
 *  1) GET  -> mostra o formulário.
 *  2) POST -> valida CSRF, procura o utilizador pelo email e confere a password.
 */
require __DIR__ . '/../../includes/inicio.php';

if (utilizador_atual()) {
    redirecionar('modulos/painel/index.php');
}

$erro  = null;
$email = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    validar_csrf();

    $email    = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';

    $utilizador = db_um(
        'SELECT id, nome, perfil, password_hash FROM utilizadores WHERE email = :email',
        [':email' => $email]
    );

    // password_verify compara a password escrita com o hash guardado na BD.
    // A mensagem é igual quer o email não exista quer a password falhe:
    // assim não revelamos quais emails estão registados.
    if ($utilizador && password_verify($password, $utilizador['password_hash'])) {
        iniciar_sessao_utilizador($utilizador);
        definir_flash('success', 'Bem-vindo de volta, ' . $utilizador['nome'] . '!');
        redirecionar('modulos/painel/index.php');
    }
    $erro = 'Email ou palavra-passe incorretos. Tenta novamente.';
}

$titulo_pagina = 'Entrar';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<div class="cartao-auth">
    <div class="text-center mb-4">
        <img src="<?= e(url('assets/img/logo.svg')) ?>" alt="Logótipo Chefy" width="88" height="88">
        <h1 class="titular mt-2">Menos caos.<br>Mais cozinha.</h1>
    </div>

    <div class="card">
        <div class="card-body p-4">
            <h2 class="h4 mb-3">Bem-vindo de volta</h2>

            <?php if ($erro): ?>
                <div class="alert alert-danger" role="alert"><?= e($erro) ?></div>
            <?php endif; ?>

            <form method="post" novalidate>
                <?= campo_csrf() ?>

                <div class="mb-3">
                    <label class="form-label" for="email">Email</label>
                    <input class="form-control" type="email" id="email" name="email"
                           value="<?= e($email) ?>" required autocomplete="email" autofocus>
                </div>

                <div class="mb-3">
                    <label class="form-label" for="password">Palavra-passe</label>
                    <input class="form-control" type="password" id="password" name="password"
                           required autocomplete="current-password">
                </div>

                <button class="btn btn-primary w-100" type="submit">Entrar</button>
            </form>
        </div>
    </div>

    <p class="text-center mt-3 mb-0">
        Ainda não tens conta? <a href="<?= e(url('modulos/auth/registo.php')) ?>">Criar conta</a>
    </p>
</div>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
