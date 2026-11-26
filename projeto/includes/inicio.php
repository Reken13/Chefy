<?php
/*
 * inicio.php — o "arranque" da aplicação.
 * TODAS as páginas começam com:  require __DIR__ . '/../../includes/inicio.php';
 * Aqui carregamos, por ordem: configuração, funções, base de dados e sessão.
 */

/** Lê uma chave do config/config.php (ex.: config('base_url')). */
function config(string $chave)
{
    static $configuracao = null;

    if ($configuracao === null) {
        $ficheiro = __DIR__ . '/../config/config.php';
        if (!is_file($ficheiro)) {
            http_response_code(500);
            exit('Falta o ficheiro config/config.php. Copie config/config.example.php para config/config.php e preencha-o.');
        }
        $configuracao = require $ficheiro;
    }
    return $configuracao[$chave];
}

// Em produção não mostramos erros técnicos ao utilizador (podem revelar segredos).
if (config('mostrar_erros')) {
    ini_set('display_errors', '1');
    error_reporting(E_ALL);
} else {
    ini_set('display_errors', '0');
    set_exception_handler(function (Throwable $erro) {
        error_log($erro);
        http_response_code(500);
        echo 'Ocorreu um erro. Tente novamente mais tarde.';
    });
}

require __DIR__ . '/funcoes.php';
require __DIR__ . '/db.php';
require __DIR__ . '/sessao.php';

iniciar_sessao();
