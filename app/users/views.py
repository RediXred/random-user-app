from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import User    
from django.http import HttpResponse, JsonResponse
from random import choice
from .services import fetch_random_users
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import redirect
from django.core.cache import cache
from django.urls import reverse
from django.contrib.messages import get_messages
from django.template.loader import render_to_string

import logging

logger = logging.getLogger(__name__)

# Create your views here.

@require_GET
def load_users_form(request):
    return render(request, 'users/load_users_form.html')

@require_GET
def user_messages(request):
    storage = get_messages(request)
    messages_html = render_to_string('users/messages.html', {'messages': storage})
    return JsonResponse({'html': messages_html})

@require_GET
def user_list(request):
    page_number = request.GET.get('page', '1')

    try:
        page_number_int = int(page_number)
        if page_number_int < 1:
            raise ValueError
    except ValueError:
        return redirect(f"{request.path}?page=1")

    users = User.objects.all().order_by('id')
    paginator = Paginator(users, 20)

    if page_number_int > paginator.num_pages and paginator.num_pages > 0:
        return redirect(f"{request.path}?page={paginator.num_pages}")

    cache_key = f"user_list_page_{page_number_int}"
    cached_response = cache.get(cache_key)
    if cached_response:
        logger.debug(f"Cache hit: {cache_key}")
        return cached_response

    page_obj = paginator.get_page(page_number_int)
    response = render(request, 'users/user_list.html', {'page_obj': page_obj})
    cache.set(cache_key, response, timeout=120)

    logger.debug(f"Cache set: {cache_key}")
    return response

def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user_detail.html', {'user': user})

def user_random(request):
    users = User.objects.all()
    if users:
        user = choice(users)
        return render(request, 'users/user_detail.html', {'user': user})
    return HttpResponse("No users available.")

@require_POST
def load_users(request):
    try:
        count = int(request.POST.get("count", 0))
        page = request.POST.get('page', '1') 
        if count > 0:
            fetch_random_users(count)
            messages.success(request, f"{count} пользователей загружено.")
            cache.clear()
        else:
            messages.error(request, "Укажите положительное количество пользователей.")
    except Exception as e:
        messages.error(request, f"Ошибка при загрузке: {e}")

    redirect_url = reverse('users:user_list') + f'?page={page}'
    print(f"Redirecting to: {redirect_url}")
    return redirect(redirect_url)