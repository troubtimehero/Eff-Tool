from django.http import HttpResponse
from django.shortcuts import render, redirect
from frequency.models import Words20000


def index(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")

    checkbox_list = ['begin']

    if request.method == 'POST':
        contain = request.POST.get('contain')
        begin = request.POST.get('begin')
        end = request.POST.get('end')
        len_min = request.POST.get('len_min')
        len_max = request.POST.get('len_max')
        len_min = int(len_min) if len_min else 0
        len_max = int(len_max) if len_max else 0

        print('*********************', begin, end, contain, len_min, len_max, sep=',')
        if begin or end or contain or len_min or len_max:
            pass
        else:
            return render(request, 'frequency/index.html', {'message': '请输入搜索条件'})

        obj = Words20000.objects.all()  # .distinct()
        if contain:
            obj = obj.filter(word__regex=r'%s' % contain)
        if begin:
            obj = obj.filter(word__regex=r'^%s' % begin)
        if end:
            obj = obj.filter(word__regex=r'%s$' % end)

        if len_max > 0:
            if len_min > len_max:
                len_min, len_max = len_max, len_min
            if len_max >= len(begin) and len_max >= len(end) and len_max >= len(contain):
                obj = obj.filter(word__regex=r'^[\S]{%s,%s}$' % (len_min, len_max))
        elif len_min > 0:
            obj = obj.filter(word__regex=r'^[\S]{%s,}$' % len_min)

        message = '共找到 %d 个单词' % obj.count()
        return render(request, 'frequency/index.html', {'words': obj, 'message': message})

    elif request.method == 'GET':
        return render(request, 'frequency/index.html')

