<?php
/*
 * funcoes.php — pequenas ferramentas usadas em várias páginas.
 */

// Unidades de medida permitidas (têm de coincidir com o ENUM da tabela ingredientes).
const UNIDADES = ['kg', 'g', 'L', 'ml', 'un'];

// Condição SQL de "stock baixo": há um mínimo definido e já estamos nele ou abaixo.
const SQL_STOCK_BAIXO = '(i.stock_minimo > 0 AND i.stock_atual <= i.stock_minimo)';

/* ---------- HTML seguro ---------- */

/** Escapa texto antes de o escrever no HTML. Evita XSS (alguém inserir <script>). */
function e($texto): string
{
    return htmlspecialchars((string) $texto, ENT_QUOTES, 'UTF-8');
}

/** Devolve ' is-invalid' se o campo tem erro (o Bootstrap pinta-o a vermelho). */
function invalido(array $erros, string $campo): string
{
    return isset($erros[$campo]) ? ' is-invalid' : '';
}

/* ---------- URLs e redirecionamentos ---------- */

/** Devolve o URL de uma página do projeto: url('modulos/auth/login.php'). */
function url(string $caminho = ''): string
{
    return rtrim(config('base_url'), '/') . '/' . ltrim($caminho, '/');
}

/** Vai para outra página do projeto e pára o script. */
function redirecionar(string $caminho): void
{
    header('Location: ' . url($caminho));
    exit;
}

/* ---------- Mensagens (aparecem uma vez, na página seguinte) ---------- */

/** $tipo: success, danger, warning ou info (cores do Bootstrap). */
function definir_flash(string $tipo, string $mensagem): void
{
    $_SESSION['flash'][] = ['tipo' => $tipo, 'mensagem' => $mensagem];
}

function obter_flashes(): array
{
    $mensagens = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $mensagens;
}

/* ---------- CSRF ----------
 * Ataque CSRF: um site malicioso faz o browser do utilizador (com sessão ativa)
 * enviar um formulário ao nosso site. Defesa: cada formulário leva um código
 * secreto que só nós conhecemos, e rejeitamos pedidos POST sem ele. */

function token_csrf(): string
{
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf'];
}

/** Escrever dentro de CADA <form method="post">:  <?= campo_csrf() ?> */
function campo_csrf(): string
{
    return '<input type="hidden" name="csrf" value="' . e(token_csrf()) . '">';
}

/** Chamar no início de qualquer página que processe um POST. */
function validar_csrf(): void
{
    $enviado = (string) ($_POST['csrf'] ?? '');
    if (!hash_equals(token_csrf(), $enviado)) {
        http_response_code(419);
        exit('Pedido inválido (CSRF). Volte atrás, recarregue a página e tente novamente.');
    }
}

/* ---------- Números e texto ---------- */

/** "1,5" ou "1.5" -> 1.5. Devolve null se não for um número. */
function para_decimal(string $valor): ?float
{
    $valor = str_replace(',', '.', trim($valor));
    return is_numeric($valor) ? (float) $valor : null;
}

/** 12.5 -> "12,5" ; 12.00 -> "12". */
function formatar_numero($numero): string
{
    $texto = number_format((float) $numero, 2, ',', '');
    return rtrim(rtrim($texto, '0'), ',');
}

/** 7.5 -> "7,50 €". */
function formatar_euro($valor): string
{
    return number_format((float) $valor, 2, ',', ' ') . ' €';
}

/** Prepara texto para um LIKE: '%' e '_' escritos pelo utilizador passam a ser literais. */
function like_seguro(string $texto): string
{
    return '%' . addcslashes($texto, '\\%_') . '%';
}

/** Só aceita pedidos POST (usado nas páginas de apagar). */
function exigir_post(): void
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        exit('Método não permitido.');
    }
}
