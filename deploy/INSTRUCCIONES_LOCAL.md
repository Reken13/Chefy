# Pasar el proyecto a tu ordenador y subirlo al servidor de la UA

**Por qué hace falta:** la sesión en la nube donde trabajamos ahora no puede ver tu ordenador ni la carpeta de red de la universidad. Para que yo pueda editar, probar y subir archivos, hay que abrir una sesión de Claude Code **que se ejecute en tu PC**. El contexto del proyecto viaja en el archivo `CLAUDE.md` de este repositorio.

## 1. Instalar (una sola vez, Windows)

| Qué | Para qué |
|---|---|
| **Git** (git-scm.com) | descargar el repositorio. Trae «Git Bash», necesario para las pruebas |
| **Claude Code**: app *Claude Desktop* (claude.ai/download) o la terminal (`claude`) | la sesión local |
| **XAMPP** (apachefriends.org) | PHP + MariaDB + phpMyAdmin |
| **VPN de la UA** | solo si estás fuera del campus, para ver `\\arca.ua.pt` |

## 2. Descargar el proyecto

En PowerShell o Git Bash:

```bash
git clone https://github.com/Reken13/Chefy.git
cd Chefy
git checkout claude/serene-archimedes-c8i9hs
```

## 3. Dejarlo funcionando en local

1. Abre el **XAMPP Control Panel** y arranca **Apache** y **MySQL**.
2. En `http://localhost/phpmyadmin` crea la base `chefy` (cotejamiento `utf8mb4_unicode_ci`) y, en *Importar*, sube primero `projeto/sql/schema.sql` y luego `projeto/sql/dados_exemplo.sql`.
3. Copia `projeto/config/config.example.php` a `projeto/config/config.php`. En XAMPP: usuario `root`, contraseña vacía.
4. Dos formas de verlo en el navegador:
   - **Sin copiar nada:** abre una terminal en la carpeta del repositorio y ejecuta `C:\xampp\php\php.exe -S localhost:8000 -t projeto` → `http://localhost:8000` (con `base_url` = `''`).
   - **Con Apache:** copia `projeto` a `C:\xampp\htdocs\projeto` → `http://localhost/projeto` (con `base_url` = `'/projeto'`).

## 4. Abrir la sesión conmigo en tu PC

Elige una de las dos:

- **Claude Desktop (la más fácil):** abre la app, ve a la pestaña **Code**, elige **Local** y selecciona la carpeta `Chefy` que acabas de clonar.
- **Terminal:** entra en la carpeta `Chefy` y ejecuta `claude remote-control`. La sesión aparecerá en la app de Claude Code (también en el móvil).

Primer mensaje sugerido: *«Lee CLAUDE.md. Arranca el servidor local, pasa tests/e2e.sh y dime si todo está bien.»*

> Opcional: en Claude Desktop → *Settings → Claude Code → Remote Control* puedes compartir la carpeta, lo que permite que una sesión en la nube la solicite. Anthropic indica que esto aún no está disponible para todas las cuentas, así que no cuentes con ello; la sesión local es la vía segura.

## 5. Subir al servidor de la UA

**Primera vez (a mano, una sola vez):**

1. En el phpMyAdmin del servidor de la UA (o con los datos que te dé el docente) importa `schema.sql` y `dados_exemplo.sql` en tu base de datos.
2. Crea en el servidor `projeto\config\config.php` copiando `config.example.php` y poniendo: los datos reales de la BD, `base_url` (probablemente `/tesp-ds-g16/projeto`; comprueba la URL con la que abres la web) y `'mostrar_erros' => false`.

**Cada vez que quieras publicar** (en PowerShell, en la raíz del repositorio):

```powershell
.\deploy\deploy.ps1              # SIMULACRO: muestra qué copiaría, no toca nada
.\deploy\deploy.ps1 -Executar    # copia de verdad
```

Si PowerShell bloquea el script: `powershell -ExecutionPolicy Bypass -File .\deploy\deploy.ps1`.

El script **no borra nada** en el servidor y **no copia** `config.php`, `.git`, `docs`, `sql`, `tests` ni `uploads`. Cuando estemos en una sesión local, yo lo ejecutaré con tu permiso: primero el simulacro y, si todo se ve bien, la subida real.

## 6. Seguridad

- **No me pegues contraseñas** de la universidad ni de la base de datos en el chat. Tu Windows ya tiene (o pide) la sesión de la carpeta de red; el script solo usa eso.
- `config.php` nunca va al Git (está en `.gitignore`).
- Antes de subir, comprueba que hay copia de seguridad de lo que ya haya en el servidor.

## 7. Qué podemos mejorar ya en local

1. Comprobar el proyecto en el servidor real (versión de PHP/MySQL, `base_url`, `.htaccess`).
2. Entrega final: API REST con JWT, perfiles y privilegios, 2FA/OTP, subida de fotos de recetas, correo (recuperar contraseña), cookies, paginación.
3. Borrar el código antiguo de Django (con tu permiso).
4. Cuando la API esté lista, conectar la app Android.
