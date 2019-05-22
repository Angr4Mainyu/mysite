from django.shortcuts import render
from django.shortcuts import redirect,HttpResponse
import json
from . import models
from .forms import UserForm, RegisterForm
import hashlib

from .cpabe import PairingGroup, CPabe_sheme
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, serialize, deserialize

attrs = ['ONE', 'TWO', 'THREE', 'FOUR']
groupObj = PairingGroup('SS512')
cpabe = CPabe_sheme(groupObj)
msk = dict()
with open('login/msk.txt', 'r') as f:
    for line in f.readlines():
        line = line.strip().split()
        msk[line[0]] = groupObj.deserialize(bytes(line[1], encoding='utf-8'))
pk = dict()
with open('login/pk.txt', 'r') as f:
    for line in f.readlines():
        line = line.strip()
        i = str.find(line, ' ')
        pk[line[:i]] = groupObj.deserialize(
            bytes(line[i+1:], encoding='utf-8'))


def index(request):
    pass
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        result = {'msg': message}
        return HttpResponse(json.dumps(result), content_type="application/json")

    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            attr = register_form.cleaned_data['attr']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())
                attr_list = attr.strip().split(',')
                for i in attr_list:
                    if i not in attrs:
                        message = '属性不合法, 属性间请用 , 间隔开。'
                        return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.attr = attr

                secretkey = cpabe.keygen(pk, msk, attr_list)
                K = str(groupObj.serialize(secretkey['K']), encoding="utf-8")
                K0 = str(groupObj.serialize(secretkey['K0']), encoding="utf-8")
                K_x = ""
                for i in range(0, len(secretkey['K_x'])):
                    K_x += str(groupObj.serialize(
                        secretkey['K_x'][attr_list[i]]), encoding="utf-8")
                    K_x += ' '

                new_user.K = K
                new_user.K0 = K0
                new_user.K_x = K_x

                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def hash_code(s, salt='mysite'):  # 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


def case_list(request):
    return render(request, 'login/case_list.html')


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")
