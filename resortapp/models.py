from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

phone_validator = RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit mobile number.")

class Customer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=10, validators=[phone_validator])
    address = models.TextField()
    id_proof = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.contact})"

class CustomerUpdateLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    old_name = models.CharField(max_length=100)
    new_name = models.CharField(max_length=100, null=True, blank=True)

    old_contact = models.CharField(max_length=10)
    new_contact = models.CharField(max_length=10, null=True, blank=True)

    old_address = models.TextField()
    new_address = models.TextField(null=True, blank=True)

    old_id_proof = models.CharField(max_length=100)
    new_id_proof = models.CharField(max_length=100, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UpdateLog({self.customer.id}) @ {self.updated_at}"

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('deluxe', 'Deluxe'),
        ('suite', 'Suite'),
    ]
    STATUS_CHOICES = [
        ('Available','Available'),
        ('Occupied','Occupied'),
        ('Maintenance','Maintenance'),
    ]
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Available")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_number} - {self.get_room_type_display()}"

class RoomHistory(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    old_type = models.CharField(max_length=20)
    new_type = models.CharField(max_length=20, null=True, blank=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RoomHistory({self.room.room_number}) @ {self.updated_at}"

class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    checkin = models.DateTimeField(default=timezone.now)
    checkout = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"BKG C:{self.customer.id} R:{self.room.room_number} ({'Active' if self.active else 'Closed'})"