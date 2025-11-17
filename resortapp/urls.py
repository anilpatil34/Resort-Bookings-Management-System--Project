from django.urls import path
from . import views

app_name = "resort"

urlpatterns = [
    path("", views.home, name="home"),
    path("add-customer/", views.add_customer, name="add_customer"),
    path("update-customer/", views.update_customer, name="update_customer"),
    path("delete-customer/", views.delete_customer, name="delete_customer"),
    path("customers/", views.customers_list, name="customers_list"),

    path("add-room/", views.add_room, name="add_room"),
    path("update-room/", views.update_room, name="update_room"),
    path("delete-room/", views.delete_room, name="delete_room"),
    path("rooms/", views.rooms_list, name="rooms_list"),

    path("checkin/", views.checkin, name="checkin"),
    path("checkout/", views.checkout, name="checkout"),

    path("search/", views.search, name="search"),
    path("billing-report/", views.billing_report, name="billing_report"),
]
