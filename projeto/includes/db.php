<?php
/*
 * db.php — acesso à base de dados (camada "abstrata" e segura).
 *
 * Regra de ouro: as páginas NUNCA juntam variáveis ao texto do SQL.
 * Escrevem marcadores (:nome) e passam os valores à parte. O PDO envia o SQL
 * e os valores separados, por isso é impossível fazer SQL Injection.
 *
 *   MAL : "SELECT * FROM ingredientes WHERE nome = '$nome'"
 *   BEM : db_um('SELECT * FROM ingredientes WHERE nome = :nome', [':nome' => $nome])
 */

/** Liga-se à BD uma única vez e devolve sempre a mesma ligação. */
function db(): PDO
{
    static $pdo = null;

    if ($pdo === null) {
        $c = config('db');
        $dsn = "mysql:host={$c['host']};dbname={$c['nome']};charset={$c['charset']}";
        $pdo = new PDO($dsn, $c['utilizador'], $c['password'], [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,  // erros SQL viram exceções
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,        // linhas como arrays
            PDO::ATTR_EMULATE_PREPARES   => false,                   // prepared statements reais
        ]);
    }
    return $pdo;
}

/** Prepara e executa uma consulta. As funções abaixo usam esta. */
function db_consulta(string $sql, array $parametros = []): PDOStatement
{
    $instrucao = db()->prepare($sql);
    $instrucao->execute($parametros);
    return $instrucao;
}

/** Devolve TODAS as linhas (array de arrays). Para listagens. */
function db_todos(string $sql, array $parametros = []): array
{
    return db_consulta($sql, $parametros)->fetchAll();
}

/** Devolve UMA linha (array) ou null se não existir. */
function db_um(string $sql, array $parametros = []): ?array
{
    $linha = db_consulta($sql, $parametros)->fetch();
    return $linha === false ? null : $linha;
}

/** INSERT / UPDATE / DELETE. Devolve o nº de linhas afetadas. */
function db_executar(string $sql, array $parametros = []): int
{
    return db_consulta($sql, $parametros)->rowCount();
}

/** Id gerado pelo último INSERT. */
function db_ultimo_id(): int
{
    return (int) db()->lastInsertId();
}
