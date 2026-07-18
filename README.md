# 🚀 TaskManager

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

A modern, responsive, and robust corporate task management ecosystem built to streamline teamwork, track project progress, and facilitate real-time asynchronous collaboration.

---

## ✨ Features At A Glance

### 📁 Project & Team Spaces
* **Workspaces:** Organise work into distinct corporate Projects and cross-functional Teams.
* **Granular Task Management:** Complete CRUD workflow for tasks with priorities (Low, Medium, High, Critical) and flexible business-driven states (`To Do`, `In Progress`, `Tech Review`, `QA`, `Rework`, `Merged`, `Deployment`, `Done`).
* **Dynamic Assignment:** Assign multiple teammates to a single task with automated text-sliced circular avatars.

### 💬 Real-Time Collaboration Layer
* **Complete Comment CRUD:** Fully independent, authorized commenting engine allowing team members to communicate inside every task card.
* **Pagination Context Protection:** Custom comment paginator that splits conversations cleanly while maintaining full task page state. Editing or deleting a comment safely returns you to your exact historical page (`?page=X`).
* **Audit Logs:** Automated `created_at` and `updated_at` timestamps showing an **(Edited)** badge with dynamic time tracking if a post changes.

### 🎨 Premium UI/UX (Tailwind CSS)
* **Smart Tab Highlighting:** Dynamic navigation matching that keeps the active workspace state illuminated even when drilling deep into secondary task forms.
* **Modern Inputs:** Responsive 100% viewport textareas with custom focus rings, smooth transitions, and subtle glass-morphism shadow effects.
* **Streamlined Control:** Cleaned and optimized drop-down user menus for both desktop layouts and mobile burger viewports.

---

## 🛠️ Tech Stack & Architecture

* **Backend Engine:** Python 3.11+ & Django Web Framework
* **Database Layer:** Object-Relational Mapping (Django ORM) with PostgreSQL / SQLite compatibility
* **Frontend UI:** Vanilla HTML5 Templates, Django Template Language (DTL), Tailwind CSS
* **Security & Auth:** Built-in Django Authentication Middleware with secure Session Management & Password Hashing algorithms

---

## ⚡ Quick Start & Installation

Get your local instance running up in less than 5 minutes:

### 1. Clone the repository & enter project directory
```bash
git clone [https://github.com/yourusername/task-manager.git](https://github.com/yourusername/task-manager.git)
cd task-manager
```

### 2. Set up and activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory of the project to manage environment-specific configurations safely. 

For the production or deployment environment, ensure you set the correct configuration module:

```bash
# Environment setup
DJANGO_SETTINGS_MODULE=task_manager.settings.dev # or prod
````

### 4. Install required packages
```bash
pip install -r requirements.txt
```

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Create your administrator account (Superuser)
```bash
python manage.py createsuperuser
```

### 7. Boot up the local development server
```bash
python manage.py runserver
```

Open your favourite browser and navigate to http://127.0.0.1:8000/. Log in with your superuser credentials and start managing!

### 💡 Key Technical Highlights (For Tech Leads & Recruiters)
Advanced Context Mixing: Overrode generic class-based views (DetailView) to cleanly integrate custom context processors, binding external interactive form structures alongside paginated database listings simultaneously.

State Preservation via URL Routing: Designed custom success URL state management logic, injecting raw HTTP query parameters dynamically across state updates to optimize web usability.

Security-First Authorization: Reinforced data mutation routes using LoginRequiredMixin and custom dataset filtering methods (get_queryset), strictly isolating cross-user access and completely preventing ID harvesting or illegal edits.
