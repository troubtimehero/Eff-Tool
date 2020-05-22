from django.http import HttpResponse
from django.shortcuts import render, redirect


def index(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")

    return render(request, 'analyse/index.html')
