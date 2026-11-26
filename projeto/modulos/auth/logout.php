<?php
/*
 * Terminar sessão. Só aceita POST com token CSRF (um link GET podia ser
 * ativado por outro site para nos deslogar).
 */
require __DIR__ . '/../../includes/inicio.php';

exigir_post();
validar_csrf();
terminar_sessao();

// A sessão foi destruída; abrimos uma nova só para poder mostrar a mensagem.
iniciar_sessao();
definir_flash('info', 'Sessão terminada. Até já!');
redirecionar('modulos/auth/login.php');
