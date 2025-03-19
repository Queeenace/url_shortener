from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import ShortenedURL
from django.views.decorators.csrf import csrf_exempt
import json
import random
import string
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404



def login_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', 'home')
        if next_url == 'login': 
            next_url = 'home'
        return redirect(next_url)

    next_url = request.GET.get('next', '/')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form, 'next_url': next_url})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

# Генерация токена
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


@login_required
def home(request):
    short_url = None
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        if original_url:
            existing_url = ShortenedURL.objects.filter(
                original_url=original_url, user=request.user).first()
            if existing_url:
                short_code = existing_url.short_code
            else:
                short_code = ShortenedURL.generate_unique_code()
                existing_url = ShortenedURL.objects.create(
                    original_url=original_url, short_code=short_code, user=request.user)

            short_url = request.build_absolute_uri(f'/{short_code}')

    urls = ShortenedURL.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home.html', {'short_url': short_url, 'urls': urls})

#API  через JSON-запрос
@csrf_exempt
def shorten_url_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            original_url = data.get("original_url")
            if not original_url:
                return JsonResponse({"error": "URL не указан"}, status=400)

            short_url_obj, created = ShortenedURL.objects.get_or_create(
                original_url=original_url, user=request.user)
            if created:
                short_url_obj.short_code = generate_short_code()
                short_url_obj.save()

            return JsonResponse({
                "original_url": short_url_obj.original_url,
                "short_code": short_url_obj.short_code,
                "short_url": request.build_absolute_uri(f"/{short_url_obj.short_code}/")
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный формат JSON"}, status=400)

    return JsonResponse({"error": "Метод не разрешен"}, status=405)


@login_required
def redirect_to_original(request, short_code):
    try:
        shortened_url = ShortenedURL.objects.get(short_code=short_code)
        shortened_url.increment_clicks()
        return redirect(shortened_url.original_url)
    except ShortenedURL.DoesNotExist:
        raise Http404("Shortened URL not found.")

def url_stats(request, short_code):
    url_entry = get_object_or_404(ShortenedURL, short_code=short_code)
    return JsonResponse({
        "original_url": url_entry.original_url,
        "short_code": url_entry.short_code,
        "click_count": url_entry.clicks,
        "created_at": url_entry.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })
