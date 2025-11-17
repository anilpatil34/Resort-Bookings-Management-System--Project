from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Customer, CustomerUpdateLog, Room, RoomHistory, Booking
from decimal import Decimal

# Home / Landing
def home(request):
    return render(request, "resortapp/home.html")

# Add Customer
def add_customer(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        contact = request.POST.get('contact', '').strip()
        address = request.POST.get('address', '').strip()
        id_proof = request.POST.get('id_proof', '').strip()

        if not (name and contact and address and id_proof):
            messages.error(request, "All fields are required.")
            return render(request, "resortapp/add_customer.html")

        if not (contact.isdigit() and len(contact) == 10):
            messages.error(request, "Contact must be a valid 10-digit number.")
            return render(request, "resortapp/add_customer.html")

        Customer.objects.create(
            name=name, contact=contact, address=address, id_proof=id_proof
        )
        messages.success(request, "Customer added successfully.")
        return redirect("resortapp:add_customer")

    return render(request, "resortapp/add_customer.html")

# Update Customer
def update_customer(request):
    if request.method == "POST":
        try:
            cid = int(request.POST.get('customer_id'))
        except (ValueError, TypeError):
            messages.error(request, "Invalid Customer ID.")
            return render(request, "resortapp/update_customer.html")

        customer = Customer.objects.filter(id=cid).first()
        if not customer:
            messages.error(request, "Customer not found.")
            return render(request, "resortapp/update_customer.html")

        name = request.POST.get('name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        id_proof = request.POST.get('id_proof')

        # Save old values
        old_name = customer.name
        old_contact = customer.contact
        old_address = customer.address
        old_id_proof = customer.id_proof

        changed = False
        # validate contact if provided
        if contact:
            if not (contact.isdigit() and len(contact) == 10):
                messages.error(request, "Contact must be a valid 10-digit number.")
                return render(request, "resortapp/update_customer.html")
            if contact != old_contact:
                customer.contact = contact
                changed = True

        if name and name != old_name:
            customer.name = name
            changed = True

        if address and address != old_address:
            customer.address = address
            changed = True

        if id_proof and id_proof != old_id_proof:
            customer.id_proof = id_proof
            changed = True

        if changed:
            customer.save()
            CustomerUpdateLog.objects.create(
                customer=customer,
                old_name=old_name, new_name=customer.name,
                old_contact=old_contact, new_contact=customer.contact,
                old_address=old_address, new_address=customer.address,
                old_id_proof=old_id_proof, new_id_proof=customer.id_proof
            )
            messages.success(request, "Customer updated and logged successfully.")
        else:
            messages.info(request, "No changes detected.")
        return redirect("resortapp:update_customer")

    return render(request, "resortapp/update_customer.html")

# Delete Customer
def delete_customer(request, customer_id=None):
    if request.method == "POST":
        cid = request.POST.get('customer_id') or customer_id
        try:
            cid = int(cid)
        except (ValueError, TypeError):
            messages.error(request, "Invalid Customer ID.")
            return redirect("resortapp:customers_list")

        customer = Customer.objects.filter(id=cid).first()
        if not customer:
            messages.error(request, "Customer not found.")
            return redirect("resortapp:customers_list")

        customer.delete()  # cascades to bookings
        messages.success(request, "Customer and related bookings deleted.")
        return redirect("resortapp:customers_list")

    # GET -> show confirm page
    ctx = {"customer_id": customer_id}
    return render(request, "resortapp/confirm_delete.html", ctx)

# Add Room
def add_room(request):
    if request.method == "POST":
        rn = request.POST.get('room_number', '').strip()
        rt = request.POST.get('room_type')
        price = request.POST.get('price')
        status = request.POST.get('status') or "Available"

        if not (rn and rt and price):
            messages.error(request, "Room number, type and price are required.")
            return render(request, "resortapp/add_room.html")

        if Room.objects.filter(room_number=rn).exists():
            messages.error(request, "Room number already exists.")
            return render(request, "resortapp/add_room.html")

        try:
            price_val = Decimal(price)
        except:
            messages.error(request, "Invalid price.")
            return render(request, "resortapp/add_room.html")

        Room.objects.create(room_number=rn, room_type=rt, price=price_val, status=status)
        messages.success(request, "Room added successfully.")
        return redirect("resortapp:add_room")

    return render(request, "resortapp/add_room.html")

# Update Room
def update_room(request):
    if request.method == "POST":
        rn = request.POST.get('room_number')
        room = Room.objects.filter(room_number=rn).first()
        if not room:
            messages.error(request, "Room not found.")
            return redirect("resortapp:rooms_list")

        old_type = room.room_type
        old_price = room.price
        old_status = room.status

        new_type = request.POST.get('room_type') or old_type
        new_price = request.POST.get('price') or old_price
        new_status = request.POST.get('status') or old_status

        changed = False
        try:
            new_price_val = Decimal(new_price)
        except:
            messages.error(request, "Invalid price.")
            return redirect("resortapp:rooms_list")

        if new_type != old_type or new_price_val != old_price or new_status != old_status:
            RoomHistory.objects.create(
                room=room,
                old_type=old_type, new_type=new_type,
                old_price=old_price, new_price=new_price_val,
                old_status=old_status, new_status=new_status
            )
            room.room_type = new_type
            room.price = new_price_val
            room.status = new_status
            room.save()
            messages.success(request, "Room updated and history logged.")
        else:
            messages.info(request, "No changes detected.")
        return redirect("resortapp:rooms_list")

    messages.error(request, "Unsupported method.")
    return redirect("resortapp:rooms_list")

# Delete Room
def delete_room(request, room_number=None):
    if request.method == "POST":
        rn = request.POST.get('room_number') or room_number
        room = Room.objects.filter(room_number=rn).first()
        if not room:
            messages.error(request, "Room not found.")
            return redirect("resortapp:rooms_list")

        # don't delete if currently booked (any active booking)
        if Booking.objects.filter(room=room, active=True).exists():
            messages.error(request, "Cannot delete room: it is currently booked.")
            return redirect("resortapp:rooms_list")

        room.delete()
        messages.success(request, "Room deleted.")
        return redirect("resortapp:rooms_list")

    return render(request, "resortapp/confirm_delete.html", {"room_number": room_number})

# Check-in
def checkin(request):
    if request.method == "POST":
        cust_id = request.POST.get('customer_id')
        room_number = request.POST.get('room_number')

        try:
            customer = Customer.objects.get(id=int(cust_id))
        except:
            messages.error(request, "Customer not found.")
            return render(request, "resortapp/checkin.html")

        room = Room.objects.filter(room_number=room_number, status='Available').first()
        if not room:
            messages.error(request, "Room not available.")
            return render(request, "resortapp/checkin.html")

        booking = Booking.objects.create(customer=customer, room=room, checkin=timezone.now(), active=True)
        room.status = 'Occupied'
        room.save()
        messages.success(request, f"Checked in. Room assigned: {room.room_number}")
        return redirect("resortapp:checkin")

    return render(request, "resortapp/checkin.html")

# Check-out
def checkout(request):
    if request.method == "POST":
        try:
            booking_id = int(request.POST.get('booking_id'))
        except:
            messages.error(request, "Invalid booking id.")
            return render(request, "resortapp/checkout.html")

        booking = Booking.objects.filter(id=booking_id, active=True).first()
        if not booking:
            messages.error(request, "Active booking not found.")
            return render(request, "resortapp/checkout.html")

        booking.checkout = timezone.now()
        # calculate bill: days stayed (round up to 1 day minimum)
        delta = booking.checkout - booking.checkin
        days = delta.days
        if delta.seconds > 0:
            days += 1
        days = max(1, days)
        booking.total_amount = Decimal(days) * booking.room.price
        booking.active = False
        booking.save()

        room = booking.room
        room.status = "Available"
        room.save()

        messages.success(request, f"Checked out. Bill: ₹{booking.total_amount} for {days} day(s).")
        return redirect("resortapp:checkout")

    return render(request, "resortapp/checkout.html")

# View lists
def customers_list(request):
    customers = Customer.objects.order_by('-created_at')
    return render(request, "resortapp/customers_list.html", {"customers": customers})

def rooms_list(request):
    rooms = Room.objects.order_by('room_number')
    return render(request, "resortapp/rooms_list.html", {"rooms": rooms})

# Search (customers & rooms)
def search(request):
    q = request.GET.get('q', '').strip()
    customers = rooms = []
    if q:
        customers = Customer.objects.filter(Q(name__icontains=q) | Q(contact__icontains=q) | Q(id__icontains=q))
        rooms = Room.objects.filter(Q(room_number__icontains=q) | Q(room_type__icontains=q) | Q(status__icontains=q))
    return render(request, "resortapp/search.html", {"query": q, "customers": customers, "rooms": rooms})

# Billing report (by booking id or customer id)
def billing_report(request):
    report = None
    if request.method == "POST":
        cust_id = request.POST.get('customer_id')
        try:
            customer = Customer.objects.get(id=int(cust_id))
        except:
            messages.error(request, "Customer not found.")
            return render(request, "resortapp/billing_report.html")

        bookings = customer.bookings.filter(active=False).order_by('-checkout')
        report = {"customer": customer, "bookings": bookings}
    return render(request, "resortapp/billing_report.html", {"report": report})
