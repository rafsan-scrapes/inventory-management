# Inventory Management App

Django-based web app for managing electronics parts inventory (refrigerators, washing machines, laptops, and their parts like motors, drain hoses, motherboards). Parts are stored in a warehouse organized by shelf/column/row.

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Django (Python), SQLite3 |
| Frontend | HTML, CSS, Vanilla JS (no frameworks, no Node.js) |
| PDF Export | ReportLab |
| Images | Pillow |
| Auth | Django built-in `django.contrib.auth` |
| Hosting | Namecheap Stellar Basic shared hosting |

## Users

Two accounts only:
- **Superuser**: can access `/admin/` (deletion happens here)
- **Normal user**: can add, edit, export

No user registration — accounts created manually via `createsuperuser` and Django admin.

## Key Design Decisions

- **Smart dropdowns**: Product Type, Brand, and Part Type show `<select>` of existing values plus "＋ Add new…" option. Picking it reveals a text input; backend creates the record if it doesn't exist.
- **AJAX cascade**: When Product Type changes on Add form, JS calls `/get-part-types/?product_type_id=X` to repopulate Part Type dropdown.
- **Product Type locked on Edit**: Changing it would orphan the PartType FK. Shown as plain text with hidden input.
- **Deletion via `/admin/` only**: Intentional friction. No delete view or button in main app.
- **PDF export is selection-based**: Checkboxes per row + "Select All". JS injects selected IDs into hidden form and POSTs to `/export/`.
- **Separate pages for Add/Edit**: ~12 fields too long for a modal.
- **`full_clean()` before save**: Triggers `Part.clean()` custom validation plus Django's `validate_unique()`.

## Data Models

### ProductType
- `name` (unique)

### Brand
- `name` (unique)

### PartType
- `name`
- `product_type` (FK to ProductType)
- Unique together: (name, product_type)

### Part
- `product_type` (FK to ProductType, PROTECT)
- `brand` (FK to Brand, PROTECT)
- `part_type` (FK to PartType, PROTECT)
- `image` (optional)
- `total_new` (PositiveIntegerField, required, default 0)
- `total_used` (PositiveIntegerField, required, default 0)
- `size_kg` (optional)
- `model_number` (optional)
- `shelf_number` (required)
- `column_number` (required)
- `row_number` (required)
- `notes` (optional)

Unique together:
- (product_type, brand, part_type)
- (shelf_number, column_number, row_number)

## Validation Rules

- `total_new` and `total_used` cannot BOTH be 0
- `part_type.product_type` must equal `part.product_type`
- Call `full_clean()` before `save()` on Part instances

## URL Map

| URL | Name | View |
|---|---|---|
| `/` | `dashboard-index` | `index` — Part list + filter + export |
| `/add/` | `add-part` | `part` — Add new part |
| `/part/edit/<pk>` | `edit-part` | `edit_part` — Edit existing part |
| `/get-part-types/` | `get-part-types` | `get_part_types` — AJAX, returns JSON |
| `/export/` | `export-pdf` | `export_pdf` — POST, returns PDF |
| `/login/` | `user-login` | Django LoginView |
| `/logout/` | `user-logout` | Django LogoutView (POST only) |
| `/admin/` | — | Django admin |

## Project Structure

```
inventory_project/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── inventory/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── pdf_utils.py
├── templates/
│   ├── partials/
│   │   ├── base.html
│   │   └── nav.html
│   ├── dashboard/
│   │   ├── index.html
│   │   ├── add_part.html
│   │   └── edit_part.html
│   └── user/
│       ├── login.html
│       └── logout.html
└── static/
    └── style.css
```

## Code Conventions

- All views use `@login_required`
- Vanilla JS only — no libraries, no npm
- `PartForm` must never include FK fields (`product_type`, `brand`, `part_type`) — those are resolved by `_resolve_fk_fields()` in views
- FK fields are handled via select + "＋ Add new…" pattern