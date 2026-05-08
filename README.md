# ClientManager Pro 🚀

> Sistema de gestión de clientes profesional — Full-Stack Python/Flask

## ✨ Características

- **Autenticación segura** — Registro/Login con contraseñas hasheadas (Werkzeug)
- **Multi-usuario** — Cada usuario gestiona sus propios clientes (aislamiento total)
- **Dashboard Analytics** — Estadísticas en tiempo real con gráficas Chart.js
- **CRUD completo** — Agregar, editar, eliminar, cambiar estado de clientes
- **Búsqueda instantánea** — Filtro en tiempo real por nombre, email o empresa
- **Filtros y ordenamiento** — Por estado (activo/inactivo) y columnas ordenables
- **Paginación** — Navegación eficiente con 10 clientes por página
- **API REST** — Endpoints JSON completos (`/api/clients`, `/api/dashboard`)
- **Dark / Light Mode** — Tema persistente con localStorage
- **Responsive PRO** — Sidebar colapsable, navegación móvil fluida
- **Diseño Premium** — Glassmorphism, gradientes, micro-animaciones

## 🛠️ Tech Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python, Flask, SQLAlchemy ORM |
| Base de datos | SQLite (dev) / PostgreSQL (prod) |
| Frontend | HTML5, CSS3 (vanilla), JavaScript ES6 |
| Gráficas | Chart.js |
| Seguridad | Werkzeug (password hashing) |
| Deploy | Gunicorn, Render / Railway |

## 🚀 Instalación

```bash
# Clonar repositorio
git clone https://github.com/DavidGSyS/client-manager.git
cd client-manager

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py
```

Abre `http://127.0.0.1:5000` en tu navegador.

## 📡 API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/clients` | Listar clientes (con search, status, sort, page) |
| POST | `/api/clients` | Crear cliente |
| PUT | `/api/clients/<id>` | Actualizar cliente |
| DELETE | `/api/clients/<id>` | Eliminar cliente |
| GET | `/api/dashboard` | Datos analytics del dashboard |

## 📁 Estructura

```
client-manager/
├── app.py              # Backend Flask + API
├── requirements.txt    # Dependencias Python
├── Procfile            # Deploy config
├── static/
│   ├── style.css       # Design system completo
│   └── script.js       # UI interactiva
└── templates/
    ├── base.html       # Layout base (sidebar + nav)
    ├── index.html      # Dashboard principal
    ├── edit.html       # Editar cliente
    ├── login.html      # Inicio de sesión
    └── register.html   # Registro
```

## 👤 Autor

David — [Portfolio de Programación](https://github.com/DavidGSyS)

---

*Desarrollado como proyecto de portafolio Full-Stack.*
