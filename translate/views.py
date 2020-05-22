from django.http import HttpResponse
from django.shortcuts import render, redirect
from translate.tools.storage import storage


def index(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")

    if request.method == 'GET':
        if storage.re_cache_ing:
            return HttpResponse('系统繁忙，请稍后再试')
        return render(request, 'translate/index.html')

    elif request.method == 'POST':
        if storage.re_cache_ing:
            return HttpResponse('系统繁忙，请稍后再试')

        if len(request.POST) <= 1:
            return render(request, 'translate/result.html')

        words = []
        for name in request.POST:
            if 'csrfmiddlewaretoken' == name:
                continue
            words.append(request.POST[name])
        data_list = storage.get_trans_better(words=words)
        # print(data_list)
        return render(request, 'translate/result.html', locals())

