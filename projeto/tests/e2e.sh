#!/bin/bash
# Pruebas de extremo a extremo del Chefy (peticiones HTTP reales + comprobaciones en la BD).
#
# Requisitos: servidor en marcha, BD con schema.sql + dados_exemplo.sql recién importados
# y config/config.php apuntando a ella. Necesita bash y curl (Git Bash / WSL en Windows).
#
#   php -S 127.0.0.1:8099 -t projeto
#   BASE=http://127.0.0.1:8099 DBCMD="mariadb --default-character-set=utf8mb4 -N chefy" bash projeto/tests/e2e.sh
#
# En XAMPP: DBCMD="mysql -u root --default-character-set=utf8mb4 -N chefy" y BASE=http://localhost/projeto
B=${BASE:-http://127.0.0.1:8099}
DBCMD=${DBCMD:-mariadb --default-character-set=utf8mb4 -N chefy}
TMP=$(mktemp -d); J=$TMP/jar.txt
pass=0; fail=0
ok(){ if [ "$2" = "1" ]; then echo "  OK   $1"; pass=$((pass+1)); else echo "  FAIL $1"; fail=$((fail+1)); fi; }
has(){ grep -q "$1" <<<"$2" && echo 1 || echo 0; }
tok(){ curl -s -b $J -c $J "$B/$1" | grep -o 'name="csrf" value="[a-f0-9]*"' | head -1 | sed 's/.*value="//;s/"//'; }
code(){ curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo "== Acesso sem sessão =="
r=$(curl -s -o /dev/null -w "%{http_code} %{redirect_url}" $B/modulos/ingredientes/index.php); ok "ingredientes sem login -> redireciona p/ login ($r)" $(has "302.*login.php" "$r")
r=$(curl -s -o /dev/null -w "%{http_code}" -X POST $B/modulos/ingredientes/apagar.php -d id=1); ok "apagar sem login nem csrf não funciona ($r)" $([ "$r" != "200" ] && echo 1 || echo 0)

echo "== Registo =="
T=$(tok modulos/auth/registo.php)
r=$(curl -s -b $J -c $J -d "csrf=$T&nome=Ana&email=ana@x.pt&password=curta&confirmacao=outra" $B/modulos/auth/registo.php); ok "password curta e diferente rejeitada" $(has "pelo menos 8" "$r")
r=$(curl -s -b $J -c $J -d "csrf=$T&nome=Ana&email=invalido&password=segredo123&confirmacao=segredo123" $B/modulos/auth/registo.php); ok "email inválido rejeitado" $(has "email válido" "$r")
r=$(code -b $J -c $J -d "csrf=errado&nome=Ana&email=ana@x.pt&password=segredo123&confirmacao=segredo123" $B/modulos/auth/registo.php); ok "CSRF inválido -> 419 ($r)" $([ "$r" = "419" ] && echo 1 || echo 0)
curl -s -o /dev/null -b $J -c $J -d "csrf=$T&nome=Ana&email=ana@x.pt&password=segredo123&confirmacao=segredo123" $B/modulos/auth/registo.php
n=$($DBCMD -e "SELECT COUNT(*) FROM utilizadores WHERE email='ana@x.pt'"); ok "utilizador criado ($n)" $([ "$n" = "1" ] && echo 1 || echo 0)
h=$($DBCMD -e "SELECT password_hash FROM utilizadores WHERE email='ana@x.pt'"); ok "password guardada com hash (não em claro)" $(has '^\$2y\$\|^\$argon' "$h")
r=$(curl -s -b $J -c $J $B/modulos/painel/index.php); ok "após registo entra no painel" $(has "Olá, Ana" "$r")
ok "painel mostra stock baixo (Azeite)" $(has "Azeite virgem extra" "$r")

echo "== Logout / Login =="
T=$(tok modulos/painel/index.php)
r=$(code -b $J -c $J -X POST $B/modulos/auth/logout.php); ok "logout sem csrf recusado ($r)" $([ "$r" = "419" ] && echo 1 || echo 0)
curl -s -o /dev/null -b $J -c $J -d "csrf=$T" $B/modulos/auth/logout.php
r=$(curl -s -o /dev/null -w "%{http_code}" -b $J -c $J $B/modulos/painel/index.php); ok "depois do logout o painel exige login ($r)" $([ "$r" = "302" ] && echo 1 || echo 0)
T=$(tok modulos/auth/login.php)
r=$(curl -s -b $J -c $J -d "csrf=$T&email=ana@x.pt&password=errada123" $B/modulos/auth/login.php); ok "password errada rejeitada" $(has "incorretos" "$r")
r=$(curl -s -b $J -c $J -d "csrf=$T&email=nao@existe.pt&password=segredo123" $B/modulos/auth/login.php); ok "email inexistente -> mesma mensagem" $(has "incorretos" "$r")
r=$(curl -s -b $J -c $J -d "csrf=$T&email=' OR '1'='1&password=' OR '1'='1" $B/modulos/auth/login.php); ok "SQL injection no login falha" $(has "incorretos" "$r")
r=$(curl -s -L -b $J -c $J -d "csrf=$T&email=ana@x.pt&password=segredo123" $B/modulos/auth/login.php); ok "login correto entra no painel" $(has "Olá, Ana" "$r")
c=$(grep -c "chefy_g16" $J); ok "cookie de sessão com nome próprio chefy_g16" $([ "$c" -ge 1 ] && echo 1 || echo 0)
ok "cookie HttpOnly" $(has "#HttpOnly_" "$(cat $J)")

echo "== Ingredientes: CRUD + pesquisa =="
r=$(curl -s -b $J "$B/modulos/ingredientes/index.php"); ok "lista mostra 12 ingredientes" $(has "12 ingrediente(s)" "$r")
r=$(curl -s -b $J "$B/modulos/ingredientes/index.php?q=ovo"); ok "pesquisa q=ovo encontra Ovos e só 1" $(has "1 ingrediente(s)" "$r")
r=$(curl -s -b $J "$B/modulos/ingredientes/index.php?baixo=1"); ok "filtro stock baixo encontra Manteiga" $(has "Manteiga" "$r")
ok "filtro stock baixo não mostra Sal" $([ "$(has '>Sal<' "$r")" = "0" ] && echo 1 || echo 0)
r=$(curl -s -b $J "$B/modulos/ingredientes/index.php?q=%25"); ok "LIKE: '%' tratado como literal (0 resultados)" $(has "Nenhum ingrediente" "$r")
r=$(curl -s -b $J "$B/modulos/ingredientes/index.php?q=%27%20OR%201%3D1%20--%20"); ok "SQL injection na pesquisa inofensiva" $(has "Nenhum ingrediente" "$r")
r=$(curl -s -b $J "$B/modulos/ingredientes/index.php?q=%3Cscript%3Ealert(1)%3C/script%3E"); ok "XSS na pesquisa escapado" $([ "$(has '<script>alert(1)' "$r")" = "0" ] && echo 1 || echo 0)
T=$(tok modulos/ingredientes/form.php)
r=$(curl -s -b $J -d "csrf=$T&id=0&nome=&categoria_id=0&unidade=xx&stock_atual=abc&stock_minimo=-1&custo_unitario=" $B/modulos/ingredientes/form.php); ok "validação: campos inválidos mostram erros" $(has "Indica o nome" "$r")
ok "validação: unidade inválida" $(has "Escolhe uma unidade" "$r")
ok "validação: número inválido" $(has "maior ou igual a 0" "$r")
r=$(curl -s -b $J -d "csrf=$T&id=0&nome=Ovos&categoria_id=4&unidade=un&stock_atual=1&stock_minimo=1&custo_unitario=1" $B/modulos/ingredientes/form.php); ok "nome duplicado rejeitado" $(has "Já existe" "$r")
curl -s -o /dev/null -b $J -c $J -d "csrf=$T&id=0&nome=Pimenta preta&categoria_id=7&unidade=g&stock_atual=250,5&stock_minimo=100&custo_unitario=0,03" $B/modulos/ingredientes/form.php
row=$($DBCMD -e "SELECT stock_atual,custo_unitario FROM ingredientes WHERE nome='Pimenta preta'"); ok "criar com vírgula decimal ($row)" $(has "250.50.*0.03" "$row")
ID=$($DBCMD -e "SELECT id FROM ingredientes WHERE nome='Pimenta preta'")
r=$(curl -s -b $J "$B/modulos/ingredientes/form.php?id=$ID"); ok "editar: formulário vem preenchido" $(has "Pimenta preta" "$r")
curl -s -o /dev/null -b $J -d "csrf=$T&id=$ID&nome=Pimenta preta moída&categoria_id=7&unidade=g&stock_atual=50&stock_minimo=100&custo_unitario=0,03" $B/modulos/ingredientes/form.php
n=$($DBCMD -e "SELECT nome FROM ingredientes WHERE id=$ID"); ok "editar: atualizado ($n)" $(has "moída" "$n")
r=$(code -b $J -X POST -d "id=$ID" $B/modulos/ingredientes/apagar.php); ok "apagar sem csrf recusado ($r)" $([ "$r" = "419" ] && echo 1 || echo 0)
r=$(code -b $J $B/modulos/ingredientes/apagar.php); ok "apagar por GET recusado ($r)" $([ "$r" = "405" ] && echo 1 || echo 0)
curl -s -o /dev/null -b $J -c $J -d "csrf=$T&id=$ID" $B/modulos/ingredientes/apagar.php
n=$($DBCMD -e "SELECT COUNT(*) FROM ingredientes WHERE id=$ID"); ok "apagar com csrf funciona" $([ "$n" = "0" ] && echo 1 || echo 0)
OVOS=$($DBCMD -e "SELECT id FROM ingredientes WHERE nome='Ovos'")
curl -s -L -b $J -c $J -d "csrf=$T&id=$OVOS" $B/modulos/ingredientes/apagar.php > $TMP/out.html
ok "não deixa apagar ingrediente usado em receita" $(has "usado em receitas" "$(cat $TMP/out.html)")

echo "== Receitas: CRUD + pesquisa =="
r=$(curl -s -b $J "$B/modulos/receitas/index.php"); ok "lista mostra as 2 receitas" $(has "Crepes simples" "$r")
r=$(curl -s -b $J "$B/modulos/receitas/index.php?q=alho"); ok "pesquisa por ingrediente (alho) -> Massa" $(has "Massa ao alho" "$r")
ok "pesquisa por ingrediente não mostra Crepes" $([ "$(has 'Crepes simples' "$r")" = "0" ] && echo 1 || echo 0)
r=$(curl -s -b $J "$B/modulos/receitas/ver.php?id=1"); ok "detalhe com custo estimado" $(has "Custo estimado" "$r")
T=$(tok modulos/receitas/form.php)
r=$(curl -s -b $J -d "csrf=$T&id=0&titulo=&porcoes=0&tempo_preparacao_min=-5&ing_id[]=&ing_qtd[]=" $B/modulos/receitas/form.php); ok "receita sem título/ingredientes rejeitada" $(has "Indica o título" "$r")
ok "porções inválidas" $(has "entre 1 e 1000" "$r")
ok "sem ingredientes" $(has "pelo menos um ingrediente" "$r")
r=$(curl -s -b $J -d "csrf=$T&id=0&titulo=Teste&porcoes=2&tempo_preparacao_min=5&ing_id[]=1&ing_qtd[]=1&ing_id[]=1&ing_qtd[]=2" $B/modulos/receitas/form.php); ok "ingrediente repetido rejeitado" $(has "duas vezes" "$r")
r=$(curl -s -b $J -d "csrf=$T&id=0&titulo=Teste&porcoes=2&tempo_preparacao_min=5&ing_id[]=1&ing_qtd[]=abc" $B/modulos/receitas/form.php); ok "quantidade inválida rejeitada (mostra o que escreveu)" $(has 'value="abc"' "$r")
curl -s -o /dev/null -b $J -c $J -d "csrf=$T&id=0&titulo=Bolo simples&descricao=Teste&porcoes=8&tempo_preparacao_min=45&instrucoes=Misturar tudo.&ing_id[]=1&ing_qtd[]=0,5&ing_id[]=3&ing_qtd[]=4&ing_id[]=&ing_qtd[]=" $B/modulos/receitas/form.php
RID=$($DBCMD -e "SELECT id FROM receitas WHERE titulo='Bolo simples'"); n=$($DBCMD -e "SELECT COUNT(*) FROM receita_ingredientes WHERE receita_id=$RID"); ok "criar receita com 2 ingredientes (linha vazia ignorada) ($n)" $([ "$n" = "2" ] && echo 1 || echo 0)
curl -s -o /dev/null -b $J -c $J -d "csrf=$T&id=$RID&titulo=Bolo de ovo&porcoes=8&tempo_preparacao_min=45&ing_id[]=3&ing_qtd[]=6" $B/modulos/receitas/form.php
n=$($DBCMD -e "SELECT COUNT(*) FROM receita_ingredientes WHERE receita_id=$RID"); t=$($DBCMD -e "SELECT titulo FROM receitas WHERE id=$RID"); ok "editar receita: 1 ingrediente e novo título ($n, $t)" $([ "$n" = "1" ] && [ "$t" = "Bolo de ovo" ] && echo 1 || echo 0)
curl -s -o /dev/null -b $J -c $J -d "csrf=$T&id=$RID" $B/modulos/receitas/apagar.php
n=$($DBCMD -e "SELECT (SELECT COUNT(*) FROM receitas WHERE id=$RID)+(SELECT COUNT(*) FROM receita_ingredientes WHERE receita_id=$RID)"); ok "apagar receita apaga também as linhas (cascade)" $([ "$n" = "0" ] && echo 1 || echo 0)

$DBCMD -e "DELETE FROM utilizadores WHERE email='ana@x.pt'"
rm -rf "$TMP"
echo; echo "RESULTADO: $pass OK, $fail FAIL"

[ "$fail" -eq 0 ]
