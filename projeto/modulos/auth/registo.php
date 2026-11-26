<?php
/*
 * Registo de utilizadores. Fluxo:
 *  1) GET  -> formulário.
 *  2) POST -> valida os campos; se estiver tudo bem, guarda a password com hash e inicia sessão.
 */
require __DIR__ . '/../../includes/inicio.php';

if (utilizador_atual()) {
    redirecionar('modulos/painel/index.php');
}

$erros = [];                       // um erro por campo: $erros['email'] = '...'
$dados = ['nome' => '', 'email' => ''];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    validar_csrf();

    $dados['nome']  = trim($_POST['nome'] ?? '');
    $dados['email'] = trim($_POST['email'] ?? '');
    $password       = $_POST['password'] ?? '';
    $confirmacao    = $_POST['confirmacao'] ?? '';

    // --- Validação (no servidor: o HTML do browser pode ser contornado) ---
    if ($dados['nome'] === '' || mb_strlen($dados['nome']) > 100) {
        $erros['nome'] = 'Indica o teu nome (máximo 100 letras).';
    }
    if (!filter_var($dados['email'], FILTER_VALIDATE_EMAIL) || mb_strlen($dados['email']) > 150) {
        $erros['email'] = 'Indica um email válido.';
    } elseif (db_um('SELECT id FROM utilizadores WHERE email = :email', [':email' => $dados['email']])) {
        $erros['email'] = 'Já existe uma conta com este email.';
    }
    if (strlen($password) < 8) {
        $erros['password'] = 'A palavra-passe deve ter pelo menos 8 caracteres.';
    }
    if ($password !== $confirmacao) {
        $erros['confirmacao'] = 'As palavras-passe não coincidem.';
    }

    // --- Guardar ---
    if (!$erros) {
        // password_hash cria um "resumo" irreversível da password (bcrypt/argon2).
        db_executar(
            'INSERT INTO utilizadores (nome, email, password_hash) VALUES (:nome, :email, :hash)',
            [
                ':nome'  => $dados['nome'],
                ':email' => $dados['email'],
                ':hash'  => password_hash($password, PASSWORD_DEFAULT),
            ]
        );
        $id = db_ultimo_id();

        iniciar_sessao_utilizador(['id' => $id, 'nome' => $dados['nome'], 'perfil' => 'chef']);
        definir_flash('success', 'Conta criada. Vamos começar!');
        redirecionar('modulos/painel/index.php');
    }
}

$titulo_pagina = 'Criar conta';
require __DIR__ . '/../../includes/cabecalho.php';
?>

<div class="cartao-auth">
    <div class="card">
        <div class="card-body p-4">
            <h1 class="h3 mb-3">Criar conta</h1>

            <form method="post" novalidate>
                <?= campo_csrf() ?>

                <div class="mb-3">
                    <label class="form-label" for="nome">Nome</label>
                    <input class="form-control <?= isset($erros['nome']) ? 'is-invalid' : '' ?>"
                           type="text" id="nome" name="nome" maxlength="100"
                           value="<?= e($dados['nome']) ?>" required autofocus>
                    <div class="invalid-feedback"><?= e($erros['nome'] ?? '') ?></div>
                </div>

                <div class="mb-3">
                    <label class="form-label" for="email">Email</label>
                    <input class="form-control <?= isset($erros['email']) ? 'is-invalid' : '' ?>"
                           type="email" id="email" name="email" maxlength="150"
                           value="<?= e($dados['email']) ?>" required autocomplete="email">
                    <div class="invalid-feedback"><?= e($erros['email'] ?? '') ?></div>
                </div>

                <div class="mb-3">
                    <label class="form-label" for="password">Palavra-passe</label>
                    <input class="form-control <?= isset($erros['password']) ? 'is-invalid' : '' ?>"
                           type="password" id="password" name="password" required autocomplete="new-password">
                    <div class="form-text">Mínimo 8 caracteres.</div>
                    <div class="invalid-feedback"><?= e($erros['password'] ?? '') ?></div>
                </div>

                <div class="mb-3">
                    <label class="form-label" for="confirmacao">Repetir palavra-passe</label>
                    <input class="form-control <?= isset($erros['confirmacao']) ? 'is-invalid' : '' ?>"
                           type="password" id="confirmacao" name="confirmacao" required autocomplete="new-password">
                    <div class="invalid-feedback"><?= e($erros['confirmacao'] ?? '') ?></div>
                </div>

                <button class="btn btn-primary w-100" type="submit">Criar conta</button>
            </form>
        </div>
    </div>

    <p class="text-center mt-3 mb-0">
        Já tens conta? <a href="<?= e(url('modulos/auth/login.php')) ?>">Entrar</a>
    </p>
</div>

<?php require __DIR__ . '/../../includes/rodape.php'; ?>
