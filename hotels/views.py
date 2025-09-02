# hotels/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Hotel, Review, Booking, HotelPhoto
from .forms import ReviewForm, BookingForm
from django.core.mail import send_mail
from django.conf import settings

# Hotel list view
def hotel_list(request):
    hotels = Hotel.objects.all()

    # প্রতিটি হোটেলের average rating calculate
    hotel_data = []
    for hotel in hotels:
        reviews = hotel.reviews.all()
        total = reviews.count()
        avg = sum([r.rating for r in reviews])/total if total > 0 else 0
        hotel_data.append({
            "hotel": hotel,
            "avg_rating": round(avg),  # nearest integer
        })

    return render(request, "hotels/list.html", {"hotel_data": hotel_data})
# Hotel detail view
def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    photos = HotelPhoto.objects.filter(hotel=hotel)
    reviews = Review.objects.filter(hotel=hotel)
    review_form = ReviewForm()
    return render(request, "hotels/hotel_detail.html", {
        "hotel": hotel,
        "photos": photos,
        "reviews": reviews,
        "review_form": review_form,
    })

# Add review
@login_required
def add_review(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.hotel = hotel
            review.save()
            messages.success(request, "Review added successfully!")
            return redirect("hotels:detail", pk=pk)
    return redirect("hotels:detail", pk=pk)

# Edit review
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully!")
            return redirect("hotels:detail", pk=review.hotel.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, "hotels/edit_review.html", {"form": form})

# Delete review
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    hotel_id = review.hotel.pk
    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted successfully!")
        return redirect("hotels:detail", pk=hotel_id)
    return render(request, "hotels/confirm_delete.html", {"object": review})

# Hotel booking
@login_required
def book_hotel(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel

            # calculate total price (simple example: $100 per night)
            nights = (booking.check_out - booking.check_in).days
            booking.total_price = 100 * nights

            # check wallet
            if request.user.profile.wallet < booking.total_price:
                messages.error(request, "Insufficient wallet balance!")
                return redirect("hotels:detail", pk=pk)

            # Deduct wallet and confirm
            request.user.profile.wallet -= booking.total_price
            request.user.profile.save()
            booking.confirmed = True
            booking.save()

            # Send confirmation email
            send_mail(
                subject="Hotel Booking Confirmation",
                message=f"Hi {request.user.username},\n\nYour booking for {hotel.name} is confirmed!\nCheck-in: {booking.check_in}\nCheck-out: {booking.check_out}\nTotal: ${booking.total_price}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
            )

            messages.success(request, "Hotel booked successfully! Confirmation email sent.")
            return redirect("hotels:detail", pk=pk)
    else:
        form = BookingForm()
    return render(request, "hotels/book.html", {"hotel": hotel, "form": form})
