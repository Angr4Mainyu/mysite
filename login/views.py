from django.shortcuts import render
from django.shortcuts import redirect, HttpResponse
import json
from . import models
from .forms import UserForm, RegisterForm, RecordForm
import hashlib

from .cpabe import PairingGroup, CPabe_sheme
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, serialize, deserialize

attrs = ['医疗部', '门诊部', '住院部', '医务部', '护理部', '住院部', '院长']
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
    if not request.session.get('is_login', None):
        return redirect("/login")
    return render(request, 'login/index.html')


def login(request):
    if request.method == "POST":
        response = {}
        response['code'] = 0
        response['msg'] = "登陆成功"
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
                    return HttpResponse(json.dumps(response), content_type="application/json")
                else:
                    message = "密码不正确！"
                    response['code'] = 1
            except:
                message = "用户不存在！"
                response['code'] = 1
        return HttpResponse(json.dumps(response), content_type="application/json")

    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        response = {}
        response["code"] = 1
        response["msg"] = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            attr = register_form.cleaned_data['attr']
            if password1 != password2:  # 判断两次密码是否相同
                response["code"] = 1
                response["msg"] = "两次输入的密码不同！"
                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    response["code"] = 1
                    response["msg"] = '用户已经存在，请重新选择用户名！'
                    return HttpResponse(json.dumps(response), content_type="application/json")
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    response["code"] = 1
                    response["msg"] = '该邮箱地址已被注册，请使用别的邮箱！'
                    return HttpResponse(json.dumps(response), content_type="application/json")
                attr_list = attr.strip().split(',')
                for i in attr_list:
                    if i not in attrs:
                        response["code"] = 1
                        response["msg"] = '属性不合法, 属性间请用 , 间隔开。'
                        return HttpResponse(json.dumps(response), content_type="application/json")

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
                response["code"] = 0
                response["msg"] = "注册成功！"
                # 自动跳转到登录页面
                return HttpResponse(json.dumps(response), content_type="application/json")
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def hash_code(s, salt='mysite'):  # 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


# 查看单独病例
# POST 参数为 rid
def view_case(request):

    if request.method == "POST":
        record_id = request.POST.get('record_id')
        try:
            record = models.Record.objects.get(rid=record_id)
            # todo 进行属性校验，并且进行解密
            message = record.detail
        except:
            message = "病例不存在"
    result = {'code': 0, 'msg': message}
    return HttpResponse(json.dumps(result), content_type="application/json")


# 查看病例列表
# POST 参数为 page limit
def case_list(request):
    if request.method == "POST":
        print(request.POST)
        page = int(request.POST.get('page'))
        limit = int(request.POST.get('limit'))
        if models.Record.objects.all().count() < (page-1)*limit:  # 查询的范围超过了已存储的病例范围
            result = {'code': 0, 'msg': "Query failed"}
            return HttpResponse(json.dumps(result), content_type="application/json")

        record_list = models.Record.objects.all()
        total = len(record_list)
        record_list = record_list[(page-1)*limit:page*limit]
        data = []
        for i in range(0, len(record_list)):
            data.append({
                "id": record_list[i].rid,
                "name": record_list[i].name,
                "sex": record_list[i].sex,
                "age": record_list[i].age,
                "time": record_list[i].time,
            })
        result = {'code': 0,
                  'msg': "Query success",
                  'count': total,
                  'data': data}
        return HttpResponse(json.dumps(result), content_type="application/json")

    login_form = UserForm()
    return render(request, 'login/case_list.html', locals())


def add_case(request):
    if request.method == "POST":
        Record_Form = RecordForm(request.POST)
        message = "请检查填写的内容！"
        if Record_Form.is_valid():  # 获取数据
            name = Record_Form.cleaned_data['name']
            sex = Record_Form.cleaned_data['sex']
            age = Record_Form.cleaned_data['age']
            u_idcard = Record_Form.cleaned_data['idcard']
            attr = Record_Form.cleaned_data['attr']
            birthday = Record_Form.cleaned_data['birthday']
            phone = Record_Form.cleaned_data['phone']
            address = Record_Form.cleaned_data['address']
            marital_status = Record_Form.cleaned_data['marital_status']
            medical_history = Record_Form.cleaned_data['medical_history']
            medical_advice = Record_Form.cleaned_data['medical_advice']

            if False:  # 添加病例时的合法性校验
                message = "添加病例时对表单的合法性校验"
                return render(request, 'login/add_case.html', locals())
            else:
                same_id_user = models.Record.objects.filter(name=u_idcard)
                if same_id_user:  # 用户名唯一
                    message = '该用户已拥有病例,请勿重复创建'
                    return render(request, 'login/add_case.html', locals())
                attr_list = attr.strip().split(',')
                for i in attr_list:
                    if i not in attrs:
                        message = '属性不合法, 属性间请用 , 间隔开。'
                        return render(request, 'login/add_case.html', locals())

                # 当一切都OK的情况下，创建新记录

                new_record = models.User.objects.create()
                new_record.name = name
                new_record.sex = sex
                new_record.age = age
                new_record.attr = attr
                detail = {}
                detail['brithday'] = birthday
                detail['phone'] = phone
                detail['address'] = address
                detail['marital_status'] = marital_status
                detail['medical_history'] = medical_history
                detail['medical_advice'] = medical_advice

                # todo  detail加密再存储
                new_record.detail = json.dumps(detail)

                new_record.save()
                return redirect('/login')  # todo 返回添加病例成功的页面
    Record_Form = RecordForm()
    return render(request, 'login/add_case.html', locals())


def medical_record(request):
    return render(request, 'login/medical_record.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index")
