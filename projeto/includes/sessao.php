<?php
/*
 * sessao.php — sessões e autenticação.
 *
 * Uma "sessão" permite ao servidor lembrar quem é o utilizador entre páginas.
 * O browser guarda só um cookie com um código; os dados ficam no servidor.
 */

const TEMPO_INATIVIDADE = 1800; // 30 min sem atividade -> a sessão expira

function iniciar_sessao(): void
{
    // Nome PRÓPRIO e cookie limitado à nossa pasta: o servidor da UA é partilhado
    // por todos os grupos e, com o nome por omissão (PHPSESSID), as sessões
    // de uns grupos podiam misturar-se com as de outros.
    session_name('chefy_g16');
    session_set_cookie_params([
        'lifetime' => 0,                                  // morre ao fechar o browser
        'path'     => rtrim(config('base_url'), '/') . '/',
        'secure'   => !empty($_SERVER['HTTPS']),          // só por HTTPS, quando existir
        'httponly' => true,                               // JavaScript não lê o cookie
        'samesite' => 'Lax',                              // ajuda contra CSRF
    ]);
    ini_set('session.use_strict_mode', '1');              // rejeita códigos de sessão inventados
    session_start();

    $expirou = isset($_SESSION['ultima_atividade'])
        && (time() - $_SESSION['ultima_atividade']) > TEMPO_INATIVIDADE;
    if ($expirou) {
        $_SESSION = [];
        session_regenerate_id(true);
        definir_flash('warning', 'A sessão expirou por inatividade. Inicie sessão novamente.');
    }
    $_SESSION['ultima_atividade'] = time();
}

/** Utilizador com sessão iniciada: ['id'=>..,'nome'=>..,'perfil'=>..] ou null. */
function utilizador_atual(): ?array
{
    return $_SESSION['utilizador'] ?? null;
}

/** Põe no início de páginas privadas: se não há sessão, vai para o login. */
function exigir_login(): void
{
    if (utilizador_atual() === null) {
        definir_flash('warning', 'Inicie sessão para continuar.');
        redirecionar('modulos/auth/login.php');
    }
}

/** Guarda o utilizador na sessão (depois de login ou registo corretos). */
function iniciar_sessao_utilizador(array $utilizador): void
{
    session_regenerate_id(true); // novo código de sessão: evita "session fixation"
    $_SESSION['utilizador'] = [
        'id'     => (int) $utilizador['id'],
        'nome'   => $utilizador['nome'],
        'perfil' => $utilizador['perfil'],
    ];
}

/** Termina a sessão por completo. */
function terminar_sessao(): void
{
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 3600, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();
}
