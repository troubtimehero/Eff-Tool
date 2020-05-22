import logging

from django.http import HttpResponse
from django.shortcuts import render, redirect

from frequency.models import Words20000
from my_admin.forms import UploadFileForm
from translate.tools.storage import storage
import threading
from django.conf import settings


message = ''


def re_cache_thread():
    storage.re_cache()


def reload_redis(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")

    global message
    message = ''
    if request.method == 'GET':
        if storage.re_cache_remain <= 0:
            return HttpResponse('密码错误次数达上线，请明天再试')
        elif storage.can_re_cache():
            return render(request, 'my_admin/reload_redis.html')
        else:
            return HttpResponse('操作过于频繁')

    elif request.method == 'POST':
        pwd = request.POST.get('password')
        if settings.ADMIN_RELOAD_REDIS_PASSWORD == pwd:
            t = threading.Thread(target=re_cache_thread, name='re_cache')
            t.start()
            message = '正在重新加载'
            return redirect("/operator/tips/")

        else:
            storage.re_cache_remain -= 1
            if storage.re_cache_remain < 0:
                message = '不能再来啦喂！'
                return redirect("/operator/tips/")
            message = '密码错误，今天还剩 %d 次机会' % storage.re_cache_remain
            return render(request, 'my_admin/reload_redis.html', {'message': message})


def upload_words(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")

    global message
    if request.method == 'GET':
        return render(request, 'my_admin/upload_words.html')

    elif request.method == 'POST':
        pwd = request.POST.get('password')
        form = UploadFileForm(request.POST, request.FILES)
        if settings.ADMIN_UPLOAD_MYSQL_PASSWORD == pwd:
            if form.is_valid():
                file = request.FILES.get('file')
                words_list = []
                win, lost = 0, 0
                for line in file:
                    win += 1
                    word = line.decode().strip()
                    print(word)
                    words_list.append(Words20000.create(word))
                try:
                    Words20000.objects.bulk_create(words_list)  # 注意 : not bluk_create
                except Exception as e:
                    lost += 1
                    logging.error('=-=-=-=- sql insert error -=-=-=-=\n', e, '\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

                message = '上传完成！成功：%， 失败：%d' % (win, lost)
                return redirect("/operator/tips/")
            message = '文件不正确'
        else:
            message = '密码错误'
    else:
        form = UploadFileForm()
    return render(request, 'my_admin/upload_words.html', {'message': message, 'form': form})


def tips(request):
    return render(request, 'my_admin/tips.html', {'message': message})
