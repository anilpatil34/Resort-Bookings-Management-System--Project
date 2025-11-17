from django.contrib import admin
from .models import Customer, CustomerUpdateLog, Room, RoomHistory, Booking

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact", "address", "id_proof", "created_at")
    search_fields = ("name", "contact", "id_proof")

@admin.register(CustomerUpdateLog)
class CustomerUpdateLogAdmin(admin.ModelAdmin):
    list_display = ("customer", "old_name", "new_name", "updated_at")
    search_fields = ("customer__name", "old_name", "new_name")

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "price", "status", "created_at")
    list_filter = ("room_type", "status")
    search_fields = ("room_number",)

@admin.register(RoomHistory)
class RoomHistoryAdmin(admin.ModelAdmin):
    list_display = ("room", "old_type", "new_type", "old_price", "new_price", "old_status", "new_status", "updated_at")
    search_fields = ("room__room_number",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "room", "checkin", "checkout", "total_amount", "active")
    list_filter = ("active", "room__room_type")
    search_fields = ("customer__name", "room__room_number")