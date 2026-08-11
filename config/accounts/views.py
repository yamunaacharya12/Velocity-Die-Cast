from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not (full_name and email and password):
            messages.error(request, 'Please fill in all fields.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif User.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            first_name = full_name.split(' ')[0]
            last_name = ' '.join(full_name.split(' ')[1:])
            user = User.objects.create_user(username=email, email=email, password=password,
                                             first_name=first_name, last_name=last_name)
            login(request, user)
            messages.success(request, f'Welcome to Velocity, {first_name}!')
            return redirect('dashboard')

    return render(request, 'website/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        messages.error(request, 'Incorrect email or password.')

    return render(request, 'website/login.html', {'next': request.GET.get('next', '')})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('home')


@login_required
def dashboard_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()

        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.zip_code = request.POST.get('zip_code', '')
        profile.country = request.POST.get('country', 'Nepal')
        profile.save()

        messages.success(request, 'Profile updated.')
        return redirect('dashboard')

    return render(request, 'website/dashboard.html', {'profile': profile})
