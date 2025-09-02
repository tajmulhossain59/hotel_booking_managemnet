from django.urls import path
from . import views

app_name = "hotels"

urlpatterns = [
    path("", views.hotel_list, name="list"),
    path("<int:pk>/", views.hotel_detail, name="detail"),
    path("<int:pk>/book/", views.book_hotel, name="book"),
    path("review/add/<int:pk>/", views.add_review, name="add_review"),
    path("review/edit/<int:review_id>/", views.edit_review, name="edit_review"),
    path("review/delete/<int:review_id>/", views.delete_review, name="delete_review"),
]
