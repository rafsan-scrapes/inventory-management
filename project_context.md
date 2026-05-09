# Project Context Summary v3
## For: Claude Sonnet 4.6 continuation session

---

## What This Project Is

A **Django-based inventory management web app** for a company that buys and sells new/used electronics and electronic parts (e.g. refrigerators, washing machines, laptops — and their parts like motors, drain hoses, motherboards, etc.). Parts are stored in a physical warehouse with shelves, columns, and rows.

---

## Tech Stack

- **Backend:** Django (Python), SQLite3
- **Frontend:** HTML, CSS, **Vanilla JavaScript** (no frameworks, no Node.js, no npm)
- **PDF Export:** ReportLab (pure Python)
- **Image handling:** Pillow
- **Auth:** Django's built-in `django.contrib.auth`
- **Hosting:** Namecheap Stellar Basic shared hosting

---

## Current Project Structure

```
inventory_project/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── inventory/               ← project config folder
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/               ← main app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
└── templates/
    ├── dashboard/
    │   └── index.html
    ├── partials/
    │   ├── base.html
    │   └── nav.html
    └── user/
        ├── login.html
        └── logout.html
```

---

## Current Code (as of this session)

### `templates/partials/base.html`
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css" .../>
    <link rel="stylesheet" href="{% static '/style.css' %}">
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    {% include 'partials/nav.html' %}
    {% block content %}{% endblock content %}
</body>
</html>
```

### `templates/partials/nav.html`
```html
<nav>
  <a class="home-link" href="{% url 'dashboard-index' %}">
    <i id="box" class="fa-solid fa-cube"></i>Inventory Management
  </a>
  <form action="{% url 'user-logout' %}" method="post">
    {% csrf_token %}
    <button type="submit">Logout</button>
  </form>
</nav>
```

### `templates/dashboard/index.html`
```html
{% extends 'partials/base.html' %}
{% block title %} Home {% endblock %}
{% block content %}
{% if user.is_authenticated %}
  <div class="table">
    <div class="table-header">
      <div class="filter-header">
        <div class="filter-title">
          <i class="fa-solid fa-filter"></i><p>Filter Products</p>
        </div>
        <button class="add-product">+ Add Product</button>
      </div>
      <div class="filter-items">
        <form name="filter" class="filter-form">
          <div class="filter-item">
            <div class="filter-item-top">
              <label for="product">Product Type: </label>
              <select id="product" name="Product">
                <option selected>All</option>
                <option>Washing Machine</option>
              </select>
            </div>
            <div class="filter-item-bottom">
              <label for="shelf">Shelf Number:</label>
              <input type="text" id="shelf" name="Shelf">
            </div>
          </div>
          <div class="filter-item">
            <div class="filter-item-top">
              <label for="brand">Brand Type: </label>
              <select id="brand" name="brand">
                <option selected>All</option>
                <option>Bosch</option>
              </select>
            </div>
            <div class="filter-item-bottom">
              <label for="column">Column Number:</label>
              <input type="text" id="column" name="Column">
            </div>
          </div>
          <div class="filter-item">
            <div class="filter-item-top">
              <label for="part">Part Type: </label>
              <select id="part" name="Part">
                <option selected>All</option>
                <option>Drain Hose</option>
              </select>
            </div>
            <div class="filter-item-bottom">
              <label for="row">Row Number:</label>
              <input type="text" id="row" name="Row">
            </div>
          </div>
          <div class="filter-item">
            <div class="filter-item-top">
              <input type="submit" class="search-button" value="Search">
            </div>
            <div class="filter-item-bottom">
              <button class="extract-pdf">Extract PDF</button>
            </div>
          </div>
        </form>
      </div>
    </div>
    <div class="table-section">
      <table>
        <thead>
          <tr>
            <th>Id</th><th>Image</th><th>Category</th><th>Brand</th>
            <th>Part</th><th>New Parts</th><th>Used Parts</th><th>Size(kg)</th>
            <th>Model</th><th>Shelf</th><th>Column</th><th>Row</th>
            <th>Notes</th><th>Edit</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>01</td>
            <td><img src="washing-machine.jpg" alt="washing-machine"/></td>
            <td>Washing Machine</td><td>Bosch</td><td>Drain Hose</td>
            <td>5</td><td>12</td><td>19</td><td></td>
            <td>2</td><td>1</td><td>3</td><td>Rusty Insides</td>
            <td><button><i class="fa-solid fa-pen-to-square"></i></button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
{% endif %}
{% endblock content %}
```

### `templates/user/login.html`
```html
{% block title %}Login{% endblock title %}
{% block content %}
<div class="">
    <h4>Login Page</h4>
    <form method="POST">
        {% csrf_token %}
        {{ form }}
        <input class="btn btn-success" type="submit" value="Login">
    </form>
</div>
{% endblock content %}
```

### `dashboard/models.py`
```python
from django.db import models

class Part(models.Model):
    image = models.ImageField(upload_to="Part_Images", null=True)
    product_type = models.CharField(null=True)
    brand = models.CharField(null=True)
    part = models.CharField(null=True)
    size = models.IntegerField(null=True)
    model = models.CharField(null=True)
    shelf = models.IntegerField(null=True)
    row = models.IntegerField(null=True)
    column = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.product_type}--{self.brand}--{self.part}"
```
> ⚠️ This model is a placeholder/draft — it will be replaced with the proper relational model (see Models section below) once frontend design is complete.

### `dashboard/views.py`
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, "dashboard/index.html")
```

---

## Planned Models (To Replace Current Draft)

### `ProductType`
- `name` — CharField, unique=True (e.g. "Refrigerator")

### `Brand`
- `name` — CharField, unique=True (e.g. "LG")

### `PartType`
- `name` — CharField
- `product_type` — FK → ProductType
- `unique_together = ('name', 'product_type')` — "Motor" can exist for both Refrigerator and Washing Machine as separate entries

### `Part` (main inventory record)
| Field | Type | Notes |
|---|---|---|
| `product_type` | FK → ProductType | on_delete=PROTECT |
| `brand` | FK → Brand | on_delete=PROTECT |
| `part_type` | FK → PartType | on_delete=PROTECT |
| `image` | ImageField | upload_to='parts/', optional |
| `total_new` | PositiveIntegerField | default=0 |
| `total_used` | PositiveIntegerField | default=0 |
| `size_kg` | DecimalField | optional |
| `model_number` | CharField | optional |
| `shelf_number` | PositiveIntegerField | |
| `column_number` | PositiveIntegerField | |
| `row_number` | PositiveIntegerField | all three are plain integers |
| `notes` | TextField | optional |

**Model constraints:**
```python
unique_together = [
    ('product_type', 'brand', 'part_type'),
    ('shelf_number', 'column_number', 'row_number'),
]
```

**clean() validation:**
- `total_new` and `total_used` cannot BOTH be 0 at entry time
- `part_type.product_type` must equal `part.product_type` — e.g. if the Part's product type is "Refrigerator", the chosen PartType must also belong to "Refrigerator", not "Washing Machine". JS cascade enforces this on the frontend; backend clean() enforces it as a safety net.

---

## Planned URLs

| URL | Purpose |
|---|---|
| `/login/` | Login page |
| `/logout/` | POST-only logout |
| `/` | Home — part list + search/filter |
| `/add/` | Single-page add part form (AJAX-powered cascade) |
| `/edit/<pk>/` | Edit a part |
| `/export/` | POST — export selected parts to PDF |
| `/get-part-types/` | AJAX endpoint — returns part types for a given product type ID |
| `/admin/` | Superuser only — delete parts, manage users |

> ✅ The Add form is a **single page** (not two steps). Vanilla JS + AJAX handles the Part Type cascade dynamically when Product Type is selected.

---

## Key Design Decisions

**Single-page Add form with AJAX cascade.**
When Product Type is selected, JS calls `/get-part-types/?product_type_id=X` and repopulates the Part Type dropdown server-side. No page reload, no two-step flow needed.

**Smart dropdown — select or create pattern.**
Product Type, Brand, and Part Type each have:
- A `<select>` of existing values with a `＋ Add new...` option at the bottom
- JS reveals a text input when `＋ Add new...` is chosen
- Backend: if text input filled → create if not exists; if empty → use dropdown; both empty → form error

**Part Type not cascaded on the search/filter page.**
Acceptable trade-off — search shows all part types. Users filter directly.

**Separate pages for Add and Edit (not modals).**
~12 fields is too long for a modal, especially on mobile.

**ReportLab for PDF** — pure Python, no system dependencies, shared-hosting safe.

**Deletion only via /admin** — intentional friction.

**Brand independent of ProductType** — LG applies across product types.

**Product Type locked on Edit** — changing it would invalidate the PartType FK.

---

## PDF Export

- Each row in the list has a **checkbox**
- A "Select All" checkbox at the top toggles all via vanilla JS
- "Export Selected to PDF" button submits a POST to `/export/` with selected part IDs
- ReportLab generates the PDF server-side
- Max **5 parts per page** (`PDF_ROWS_PER_PAGE = 5` constant in `pdf_utils.py`, easy to change)
- PDF columns: Product Type, Brand, Part Type, New stock, Used stock, Shelf/Col/Row, Model No, Notes
- Images NOT in PDF
- Header: company name. Footer: "Page X of Y"

---

## Authentication

- Django built-in auth, no custom user model, no registration page
- Two manually created users:
  - **Superuser** — admin access, can delete
  - **Normal user** — add, edit, export only
- `LOGIN_URL = '/login/'` and `LOGOUT_REDIRECT_URL = '/login/'` in settings.py
- Logout is a `<form method="POST">` button — NOT an `<a>` tag (Django 5 rejects GET logout with 405)
- All inventory views use `@login_required`

---

## What Has Been Completed

- Project and app initialized
- Login working correctly
- Logout 405 bug fixed (GET → POST form)
- Basic index page with hardcoded filter UI and table (static/demo only)
- Basic nav with home link and logout button
- Placeholder `Part` model exists (will be replaced)

## Current Focus / Next Step

**Frontend first.** Before touching models or backend logic, the priority is to get all HTML/CSS/JS pages designed, responsive (mobile-first), and structured in a Django-template-friendly way so Python/Django functionality can be wired in cleanly afterwards. The agent should help with tweaks and new pages in this order:
1. `index.html` — filter UI + table + checkboxes for PDF export
2. `add.html` — single-page add part form with smart dropdowns
3. `edit.html` — pre-filled edit form
4. `login.html` — styled login page