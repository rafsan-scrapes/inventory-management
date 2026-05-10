from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError as ModelValidationError

from .models import Part, ProductType, Brand, PartType
from .forms import PartForm

# ── Index ──────────────────────────────────────────────────────────────────


@login_required
def index(request):
    items = Part.objects.select_related("product_type", "brand", "part_type").all()
    context = {"items": items}
    return render(request, "dashboard/index.html", context=context)


# ── AJAX: Part-type cascade ────────────────────────────────────────────────


@login_required
def get_part_types(request):
    """
    GET /get-part-types/?product_type_id=<id>
    Returns JSON list of PartTypes for the given ProductType.
    Called by the add/edit form's JS when Product Type changes.
    """
    product_type_id = request.GET.get("product_type_id", "").strip()
    part_types = []
    if product_type_id:
        part_types = list(
            PartType.objects.filter(product_type_id=product_type_id)
            .values("id", "name")
            .order_by("name")
        )
    return JsonResponse({"part_types": part_types})


# ── Smart-dropdown FK resolution ───────────────────────────────────────────


def _resolve_fk_fields(post_data):
    """
    Extract and resolve product_type, brand, and part_type from the smart-dropdown
    POST fields.  Each FK can come from either a select (existing record) or a
    text input (new value to create).

    Returns: (product_type, brand, part_type, errors)
      - Any resolved object may be None when its errors key is set.
      - errors is a plain dict: field_name → error string (or 'non_field_errors' → list).
    """
    errors = {}
    product_type = brand = part_type = None

    # ── Product Type ──────────────────────────────────────────────────────
    new_pt_name = post_data.get("new_product_type", "").strip()
    pt_id = post_data.get("product_type_select", "").strip()

    if new_pt_name:
        product_type, _ = ProductType.objects.get_or_create(name=new_pt_name)
    elif pt_id:
        try:
            product_type = ProductType.objects.get(pk=pt_id)
        except (ProductType.DoesNotExist, ValueError):
            errors["product_type"] = "Invalid product type selected."
    else:
        errors["product_type"] = "Product type is required."

    # ── Brand ──────────────────────────────────────────────────────────────
    new_brand_name = post_data.get("new_brand", "").strip()
    brand_id = post_data.get("brand_select", "").strip()

    if new_brand_name:
        brand, _ = Brand.objects.get_or_create(name=new_brand_name)
    elif brand_id:
        try:
            brand = Brand.objects.get(pk=brand_id)
        except (Brand.DoesNotExist, ValueError):
            errors["brand"] = "Invalid brand selected."
    else:
        errors["brand"] = "Brand is required."

    # ── Part Type ──────────────────────────────────────────────────────────
    new_ptype_name = post_data.get("new_part_type", "").strip()
    ptype_id = post_data.get("part_type_select", "").strip()

    if new_ptype_name:
        if product_type:
            part_type, _ = PartType.objects.get_or_create(
                name=new_ptype_name,
                product_type=product_type,
            )
        else:
            errors["part_type"] = (
                "Select or enter a product type before adding a new part type."
            )
    elif ptype_id:
        try:
            part_type = PartType.objects.get(pk=ptype_id)
        except (PartType.DoesNotExist, ValueError):
            errors["part_type"] = "Invalid part type selected."
    else:
        errors["part_type"] = "Part type is required."

    return product_type, brand, part_type, errors


# ── Add part ───────────────────────────────────────────────────────────────


@login_required
def part(request):
    product_types = ProductType.objects.all().order_by("name")
    brands = Brand.objects.all().order_by("name")

    if request.method == "POST":
        product_type, brand, part_type, fk_errors = _resolve_fk_fields(request.POST)
        form = PartForm(request.POST, request.FILES)

        if not fk_errors and form.is_valid():
            part_instance = form.save(commit=False)
            part_instance.product_type = product_type
            part_instance.brand = brand
            part_instance.part_type = part_type

            # Run full model validation (calls Part.clean() + validate_unique()).
            # This catches the "both stocks are 0" rule and the part_type ↔
            # product_type mismatch, as well as unique_together violations.
            try:
                part_instance.full_clean()
                part_instance.save()
                return redirect("dashboard-index")
            except ModelValidationError as exc:
                if hasattr(exc, "message_dict"):
                    for field, msgs in exc.message_dict.items():
                        if field == "__all__":
                            fk_errors["non_field_errors"] = msgs
                        else:
                            fk_errors[field] = msgs
                else:
                    fk_errors["non_field_errors"] = exc.messages

        # Re-populate part-type dropdown for the selected product type so the
        # user doesn't lose their selection on error re-render.
        selected_pt_id = request.POST.get("product_type_select", "").strip()
        selected_part_types = []
        if selected_pt_id and selected_pt_id != "__new__":
            selected_part_types = list(
                PartType.objects.filter(product_type_id=selected_pt_id)
                .values("id", "name")
                .order_by("name")
            )

        context = {
            "form": form,
            "product_types": product_types,
            "brands": brands,
            "fk_errors": fk_errors,
            "posted": request.POST,
            "selected_part_types": selected_part_types,
        }
        return render(request, "dashboard/add_part.html", context=context)

    # GET
    context = {
        "form": PartForm(),
        "product_types": product_types,
        "brands": brands,
        "fk_errors": {},
        "posted": {},
        "selected_part_types": [],
    }
    return render(request, "dashboard/add_part.html", context=context)


# ── Edit part ──────────────────────────────────────────────────────────────


@login_required
def edit_part(request, pk):
    """Edit an existing part."""
    item = get_object_or_404(
        Part.objects.select_related("product_type", "brand", "part_type"), pk=pk
    )

    product_types = ProductType.objects.all().order_by("name")
    brands = Brand.objects.all().order_by("name")
    part_types_for_product = PartType.objects.filter(
        product_type=item.product_type
    ).order_by("name")

    if request.method == "POST":
        posted = request.POST.copy()

        # Lock product type so it cannot be changed during edit.
        posted["product_type_select"] = str(item.product_type_id)
        posted.pop("new_product_type", None)

        product_type, brand, part_type, fk_errors = _resolve_fk_fields(posted)
        form = PartForm(request.POST, request.FILES, instance=item)

        if not fk_errors and form.is_valid():
            part_instance = form.save(commit=False)
            part_instance.product_type = item.product_type
            part_instance.brand = brand
            part_instance.part_type = part_type

            try:
                part_instance.full_clean()
                part_instance.save()
                return redirect("dashboard-index")

            except ModelValidationError as exc:
                if hasattr(exc, "message_dict"):
                    for field, msgs in exc.message_dict.items():
                        fk_errors[
                            "non_field_errors" if field == "__all__" else field
                        ] = msgs
                else:
                    fk_errors["non_field_errors"] = exc.messages

        return render(
            request,
            "dashboard/edit_part.html",
            {
                "form": form,
                "item": item,
                "product_types": product_types,
                "brands": brands,
                "part_types_for_product": part_types_for_product,
                "fk_errors": fk_errors,
                "posted": posted,
            },
        )

    return render(
        request,
        "dashboard/edit_part.html",
        {
            "form": PartForm(instance=item),
            "item": item,
            "product_types": product_types,
            "brands": brands,
            "part_types_for_product": part_types_for_product,
            "fk_errors": {},
            "posted": {},
        },
    )
