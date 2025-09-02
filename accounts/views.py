from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile
from decimal import Decimal

# Email activation imports
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

# Registration view with email activation
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email verified
            user.set_password(form.cleaned_data["password"])
            user.save()
            # Create Profile
            Profile.objects.create(user=user)
            
            # Send activation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Hotel Booking account'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            
            messages.success(request, 'Please check your email to activate your account.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

# Activation view
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated!")
        return redirect('accounts:profile')
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('accounts:login')

# Profile view
@login_required
def profile(request):
    return render(request, "accounts/profile.html")

# Deposit wallet
@login_required
def deposit_wallet(request):
    if request.method == "POST":
        amount = Decimal(request.POST.get("amount"))
        request.user.profile.wallet += amount
        request.user.profile.save()
        messages.success(request, f"${amount} added to wallet.")
        return redirect("accounts:profile")
    return render(request, "accounts/deposit.html")
