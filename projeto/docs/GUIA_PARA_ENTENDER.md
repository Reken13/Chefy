# Guía para entender el código (en español, para estudiar)

> Este archivo es **solo para ti**: te explica cómo funciona el proyecto para que puedas defenderlo.
> La documentación que entregues al docente va en portugués (`docs/BASE_DE_DADOS.md` y el `README.md`).
> Los comentarios del código están en español para que los puedas leer; si el docente los quiere en portugués, es una tarea sencilla de hacer al final.

## 1. El mapa del proyecto

```
projeto/
├── index.php                 → "puerta de entrada": te manda al login o al panel
├── config/
│   ├── config.example.php    → plantilla de configuración (SÍ va a Git)
│   └── config.php            → TU configuración real, con la contraseña de la BD (NO va a Git)
├── includes/                 → código compartido, nunca se abre directamente en el navegador
│   ├── inicio.php            → "arranque": carga todo lo demás. Toda página empieza con él
│   ├── db.php                → hablar con la base de datos (de forma segura)
│   ├── sessao.php            → sesiones y login
│   ├── funcoes.php           → herramientas pequeñas (escapar HTML, CSRF, formatear números…)
│   ├── cabecalho.php         → parte de arriba del HTML (menú, mensajes)
│   └── rodape.php            → parte de abajo del HTML (scripts)
├── modulos/                  → las pantallas, una carpeta por tema ("modular")
│   ├── auth/       login.php · registo.php · logout.php
│   ├── painel/     index.php
│   ├── ingredientes/  index.php (listar+buscar) · form.php (crear/editar) · apagar.php
│   └── receitas/   index.php · ver.php · form.php · apagar.php
├── assets/                   → CSS, JavaScript (jQuery) e imágenes
└── sql/                      → schema.sql (tablas) y dados_exemplo.sql (datos de prueba)
```

**Idea clave:** cada archivo de `modulos/` es una página. Todas siguen el mismo esquema:

```php
<?php
require '.../includes/inicio.php';   // 1. arranque (config, BD, sesión)
exigir_login();                      // 2. ¿hay que estar logueado? (en páginas privadas)

// 3. LÓGICA: leer parámetros, consultar la BD, procesar el formulario si es POST

$titulo_pagina = '...';
require '.../includes/cabecalho.php'; // 4. dibuja la parte de arriba
?>
<!-- 5. HTML de la página, mezclado con <?= e($dato) ?> para mostrar datos -->
<?php require '.../includes/rodape.php'; ?>   // 6. dibuja la parte de abajo
```

Primero va la lógica y después el HTML. Así, si hay que redirigir (`header('Location…')`), todavía no se ha enviado nada al navegador.

## 2. El recorrido de una petición (ejemplo: crear un ingrediente)

1. Pulsas «+ Novo ingrediente» → el navegador pide `form.php` por **GET** → el PHP muestra el formulario vacío.
2. Rellenas y pulsas «Guardar» → el navegador envía el formulario por **POST** a `form.php`.
3. `form.php` comprueba el **token CSRF**, **valida** cada campo y:
   - si hay errores → vuelve a mostrar el formulario con los errores y lo que escribiste;
   - si todo está bien → hace el `INSERT`, guarda un mensaje y **redirige** a la lista.
4. La redirección tras un POST (patrón *Post/Redirect/Get*) evita que, al refrescar con F5, se reenvíe el formulario y se duplique el ingrediente.

**CRUD** = Create (crear), Read (leer/listar/buscar), Update (editar), Delete (borrar). Aquí:

| Letra | Ingredientes | Recetas |
|---|---|---|
| C | `form.php` (sin `id`) | `form.php` (sin `id`) |
| R | `index.php` (+ filtros) | `index.php` y `ver.php` |
| U | `form.php?id=5` | `form.php?id=5` |
| D | `apagar.php` | `apagar.php` |

## 3. Seguridad: qué hay y dónde (te lo preguntarán en la defensa)

| Amenaza | Qué es | Defensa | Dónde |
|---|---|---|---|
| **SQL Injection** | Escribir SQL malicioso en un campo (`' OR '1'='1`) | Consultas preparadas: el SQL y los valores van separados | `includes/db.php` (y todas las consultas usan `:marcador`) |
| **XSS** | Insertar `<script>` en un texto que luego se muestra a otros | Escapar siempre con `e()` al imprimir | `includes/funcoes.php` → `e()` |
| **Contraseñas robadas** | Si roban la BD, ven las contraseñas | Guardar solo un *hash* con `password_hash`; comparar con `password_verify` | `registo.php`, `login.php` |
| **CSRF** | Otra web hace que tu navegador envíe un formulario a nuestra web | Token secreto en cada formulario POST | `campo_csrf()` / `validar_csrf()` |
| **Session fixation** | Fijar el id de sesión de la víctima | `session_regenerate_id(true)` al iniciar sesión | `includes/sessao.php` |
| **Robo de cookie** | Leer la cookie con JavaScript | `HttpOnly` + `SameSite` (+ `Secure` con HTTPS) | `includes/sessao.php` |
| **Páginas privadas abiertas** | Entrar sin login escribiendo la URL | `exigir_login()` al inicio de cada página privada | todas las de `modulos/` |
| **Borrar por enlace** | Un `<img src="apagar.php?id=3">` borraría datos | Borrar solo por POST + CSRF | `apagar.php` |
| **Sesión abandonada** | Alguien usa un PC desatendido | Expira a los 30 min sin actividad | `includes/sessao.php` |
| **Revelar usuarios** | Distinguir «email no existe» de «contraseña mal» | Mismo mensaje en ambos casos | `login.php` |
| **Mezcla con otros grupos** | El servidor de la UA es compartido | Cookie de sesión con nombre y ruta propios | `includes/sessao.php` |

> Importante: validar en el navegador (atributos HTML como `required`) es solo comodidad. **La validación de verdad se hace en PHP**, porque alguien puede saltarse el HTML.

## 4. jQuery: qué hace (`assets/js/chefy.js`)

- Pide confirmación antes de borrar (`data-confirmar`).
- Aplica los filtros de ingredientes al cambiar el desplegable.
- En el formulario de recetas, añade/quita filas de ingredientes (copia un molde `<template>`).

Todo lo importante funciona también sin JavaScript, salvo añadir más de una fila de ingredientes.

## 5. Cómo ejecutarlo

### En tu ordenador (Windows)

1. Instala **XAMPP** (o Laragon). Arranca Apache y MySQL.
2. Copia la carpeta `projeto` a `C:\xampp\htdocs\projeto`.
3. Abre `http://localhost/phpmyadmin` → crea una base de datos `chefy` (cotejamiento `utf8mb4_unicode_ci`) → pestaña *Importar* → sube `sql/schema.sql` y después `sql/dados_exemplo.sql`.
4. Copia `config/config.example.php` a `config/config.php`. En XAMPP el usuario es `root` y la contraseña vacía. Pon `'base_url' => '/projeto'`.
5. Abre `http://localhost/projeto/` y crea tu cuenta con «Criar conta».

### Si tienes PHP instalado (sin XAMPP)

```bash
php -S localhost:8000 -t projeto      # base_url = ''
```

### En el servidor de la universidad

1. Pide/consulta en el phpMyAdmin del servidor los datos de tu base de datos (host, nombre, usuario, contraseña).
2. Importa `sql/schema.sql` y `sql/dados_exemplo.sql` en esa base.
3. Copia el **contenido** de `projeto/` a `\\arca.ua.pt\Hosting\esan-tesp-ds-paw.web.ua.pt\tesp-ds-g16\projeto`.
4. En el servidor crea `config/config.php` con los datos reales y el `base_url` correcto (probablemente `/tesp-ds-g16/projeto`; compruébalo mirando la URL con la que abres la web), y `'mostrar_erros' => false`.
5. No copies el `config.php` de tu ordenador: tiene credenciales locales.

## 6. Qué cubre esto de la rúbrica (1ª entrega: 6 valores)

| Criterio | Dónde está |
|---|---|
| CRUD / pesquisa de entidades (2) | Ingredientes y Receitas completos, con búsqueda y filtros |
| Base de dados: modelos, diagramas, explicação (1) | `sql/schema.sql` + `docs/BASE_DE_DADOS.md` |
| Registo/Login e sessões (2) | `modulos/auth/` + `includes/sessao.php` |
| Interação segura e abstrata com a BD (1) | `includes/db.php` (PDO + consultas preparadas + transacciones) |

## 7. Lo que NO está hecho todavía (entrega final) y dudas para el docente

**Falta para la entrega final:** cookies propias (p. ej. «recordar sesión»), subida de ficheiros (foto de la receta), envío de correo (recuperar contraseña), API REST con JWT para la app móvil, perfiles/privilegios (la columna `perfil` existe pero aún no se usa para restringir nada), 2FA/OTP, paginación de listados, y documentación final.

**Cosas que no puedo saber desde aquí y debes comprobar:**
- La diapositiva dice «aplicação modular (conforme trabalhado nas aulas)». **No he visto el material de las clases.** Compara esta estructura con la que enseñó el docente y ajústala si difiere (nombres de carpetas, uso de plantillas, etc.).
- Qué versión de PHP y de MySQL/MariaDB tiene el servidor de la UA. Yo solo he podido probarlo con PHP 8.3; está escrito para funcionar desde PHP 7.4 (sin probar). Usa `CHECK` en MySQL ≥ 8.0.16 / MariaDB ≥ 10.2 (en versiones anteriores MySQL ignora los `CHECK` sin dar error; la validación de PHP sigue protegiendo los datos).
- Que se permiten las librerías por CDN (Bootstrap, jQuery, Google Fonts). La diapositiva las admite como tecnologías, pero si el docente exige que sean locales, basta descargarlas a `assets/`.
- Qué esperan en «IA condicionada»: la diapositiva pide que **tú asumas la autoría**. Asegúrate de entender cada archivo (esta guía te ayuda) y de poder explicar cualquier línea.
