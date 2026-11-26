<?php
/*
 * Ponto de entrada: se há sessão vai para o painel, senão para o login.
 */
require __DIR__ . '/includes/inicio.php';

redirecionar(utilizador_atual() ? 'modulos/painel/index.php' : 'modulos/auth/login.php');
