from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django import forms

from .models import UserProfile
from farms.models import Farm, Crop


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'Username or email', 'autofocus': True}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'fp-input', 'placeholder': 'Password'}),
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'Desired username'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'fp-input', 'placeholder': 'farmer@farmpulse.mw'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'fp-input', 'placeholder': 'At least 8 characters'}),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'fp-input', 'placeholder': 'Repeat password'}),
    )
    farm_name = forms.CharField(
        max_length=120,
        initial="Chitukuko Farm",
        widget=forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'e.g. Tikondane Farm'}),
    )
    district = forms.CharField(
        max_length=80,
        initial="Lilongwe",
        widget=forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'e.g. Lilongwe, Kasungu, Salima'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        username = cleaned_data.get('username')

        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'Passwords do not match.')

        if username and User.objects.filter(username__iexact=username).exists():
            self.add_error('username', 'This username is already taken.')

        return cleaned_data


def ensure_database_ready():
    """Self-healing safety net: automatically runs migrations and seeds demo accounts."""
    try:
        from django.db import connection
        from django.core.management import call_command
        tables = connection.introspection.table_names()
        if 'auth_user' not in tables:
            call_command('migrate', interactive=False)

        import runpy
        from django.contrib.auth.models import User

        # Ensure naffe account is fully seeded & password verified
        naffe = User.objects.filter(username='naffe').first()
        if not naffe:
            runpy.run_module('seed_naffe', run_name='__main__')
        else:
            if not naffe.check_password('Password123!'):
                naffe.set_password('Password123!')
                naffe.is_active = True
                naffe.save()

        # Ensure miriam account is fully seeded & password verified
        miriam = User.objects.filter(username='miriam').first()
        if not miriam:
            runpy.run_module('seed_miriam_chiphaka', run_name='__main__')
        else:
            if not miriam.check_password('Password123!'):
                miriam.set_password('Password123!')
                miriam.is_active = True
                miriam.save()
    except Exception as exc:
        print(f"[FarmPulse DB Auto-init Error]: {exc}")


def user_login(request):
    ensure_database_ready()
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next', 'home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username']
            pwd = form.cleaned_data['password']

            # Support login by email or username
            user_obj = User.objects.filter(email__iexact=uname).first()
            username_to_auth = user_obj.username if user_obj else uname

            user = authenticate(request, username=username_to_auth, password=pwd)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(request.POST.get('next') or next_url or 'home')
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {
        'form': form,
        'next': next_url,
    })


def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            farm_name = form.cleaned_data['farm_name']
            district = form.cleaned_data['district']

            # 1. Create User
            user = User.objects.create_user(username=username, email=email, password=password)

            # 2. Create Profile
            UserProfile.objects.create(
                user=user,
                preferred_district=district,
            )

            # 3. Create initial Farm
            farm = Farm.objects.create(
                owner=user,
                name=farm_name,
                location_description=f"{district}, Malawi",
                total_land_ha=Decimal('2.50'),
                cultivated_land_ha=Decimal('2.00'),
                irrigation_type='rainfed',
                soil_type='sandy_clay_loam',
            )
            # Add popular staple crops to preferred
            maize = Crop.objects.filter(slug='maize').first()
            gnuts = Crop.objects.filter(slug='groundnuts').first()
            if maize:
                farm.preferred_crops.add(maize)
            if gnuts:
                farm.preferred_crops.add(gnuts)

            # 4. Authenticate & Log in
            login(request, user)
            messages.success(request, f"Account created! Welcome to FarmPulse, {username}.")
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {
        'form': form,
    })


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


def user_password_reset(request):
    """
    Demo password reset flow with simulated notification.
    """
    submitted = False
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            messages.success(request, f"If an account exists for {email}, password reset instructions have been sent.")
            submitted = True

    return render(request, 'registration/password_reset.html', {
        'submitted': submitted,
    })
