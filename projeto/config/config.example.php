<?php
/*
 * Configuração do Chefy.
 *
 * COMO USAR: copiar este ficheiro para "config.php" (na mesma pasta) e
 * preencher os valores. O config.php NÃO vai para o Git (tem a password da BD).
 */
return [
    // Dados da base de dados (no servidor da UA: os que o phpMyAdmin/docente indicar).
    'db' => [
        'host'       => 'localhost',
        'nome'       => 'chefy',
        'utilizador' => 'root',
        'password'   => '',
        'charset'    => 'utf8mb4',
    ],

    // Caminho onde o projeto está publicado, SEM barra final.
    //   Em local (php -S):        ''
    //   Exemplo no servidor UA:   '/tesp-ds-g16/projeto'   (confirmar o caminho real)
    'base_url' => '',

    // true só durante o desenvolvimento. No servidor final: false.
    'mostrar_erros' => true,
];
