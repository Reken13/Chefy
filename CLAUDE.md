# Chefy — contexto del proyecto

Proyecto escolar (UA · Programação Ambiente Web, grupo G16). **El autor es el alumno, no Claude.**
Es una aplicación de gestión de cocina vista desde el chef. Idioma de la interfaz: portugués europeo.

## Reglas obligatorias

- **Sin atribución de IA:** no añadir `Co-Authored-By`, enlaces de sesión ni menciones a Claude/Anthropic en commits, código, comentarios ni documentación. Los commits van a nombre del alumno.
- **Solo PHP + MySQL/MariaDB + HTML/CSS (Bootstrap) + JavaScript (jQuery).** Prohibidos frameworks o stacks que sustituyan esa arquitectura (Laravel, Symfony, Django, React, etc.). Tailwind/DaisyUI están permitidos por el enunciado, pero el proyecto usa Bootstrap.
- **El alumno debe poder explicar todo el código.** Prioriza código simple y legible, con comentarios en español. Nada de abstracciones innecesarias.
- No pegar nunca contraseñas ni credenciales en el chat, el código o el Git. `projeto/config/config.php` está en `.gitignore`.
- Antes de subir al servidor o borrar algo, pedir confirmación.

## Dónde está cada cosa

- `projeto/` → la aplicación web (se copia tal cual a `...\tesp-ds-g16\projeto` en el servidor). Guía: `projeto/docs/GUIA_PARA_ENTENDER.md`.
- `deploy/deploy.ps1` → sube `projeto/` al servidor (PowerShell, simulacro por defecto).
- `projeto/tests/e2e.sh` → 47 pruebas HTTP (login, CRUD, CSRF, SQLi, XSS…). Ejecutarlas tras cada cambio.
- Resto de carpetas en la raíz (`core/`, `recipes/`, `templates/`, `manage.py`…) = **versión antigua en Django, descartada** por no cumplir el enunciado. No tocar; pendiente de borrar con permiso del alumno.
- La app Android (`chefyV1Android`, Kotlin/Compose) está aparte y consumirá una API REST en PHP con JWT (entrega final).

## Convenciones del código PHP

- Cada página: `require includes/inicio.php` → `exigir_login()` → lógica → `cabecalho.php` → HTML → `rodape.php`.
- SQL **siempre** con marcadores (`:nombre`) vía `db_todos / db_um / db_executar`. Con prepared statements reales un marcador no puede repetirse en la misma consulta.
- Todo texto de usuario impreso con `e()`. Todo formulario POST con `campo_csrf()` y `validar_csrf()`. Borrados solo por POST.
- Tras un POST correcto: `definir_flash()` + `redirecionar()`.

## Entrega

- 1.ª entrega (6 val.): CRUD/pesquisa, BD con diagramas y explicación, registo/login/sessões, acesso seguro à BD → **hecho**.
- Entrega final (14 val.): cookies/uploads/mail, API REST + JWT + interacción móvil, segurança (perfis, privilégios, 2FA/OTP), funcionalidades, complexidade, design, documentação → **pendiente**.
- Duda abierta: el enunciado dice «modular, conforme trabalhado nas aulas»; no se ha visto el material de clase. Comparar con la estructura del docente.

## Probar en local

```
mariadb -e "CREATE DATABASE chefy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
mariadb chefy < projeto/sql/schema.sql && mariadb chefy < projeto/sql/dados_exemplo.sql
cp projeto/config/config.example.php projeto/config/config.php   # y editar credenciales
php -S 127.0.0.1:8099 -t projeto
bash projeto/tests/e2e.sh
```
