from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard-index"),
    path("part/edit/<int:pk>", views.edit_part, name="edit-part"),
]
