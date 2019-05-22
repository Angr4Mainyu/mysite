from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    attr = forms.CharField(label="属性", max_length=1024, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(
        attrs={'class': 'form-control'}))


class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))


class RecordForm(forms.Form):
    gender = (
        ('male', '男'),
        ('female', '女'),
    )
    ismarried = (
        ('single', '未婚'),
        ('married', '已婚'),
    )
    name = forms.CharField(label="姓名", max_length=128, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label='性别', choices=gender)
    age = forms.IntegerField(label="年龄", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    idcard = forms.IntegerField(
        label="身份证号", widget=forms.TextInput(attrs={'class': 'form-control'}))
    attr = forms.CharField(label="属性", max_length=1024, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    birthday = forms.DateField(
        label="出生日期", widget=forms.DateInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="手机号", max_length=20, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    address = forms.CharField(label="地址", max_length=128, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    marital_status = forms.ChoiceField(label="婚姻状况", choices=ismarried)
    medical_history = forms.CharField(
        label="病史", max_length=1024, widget=forms.TextInput(attrs={'class': 'form-control'}))
    medical_advice = forms.CharField(
        label="医生意见", max_length=1024, widget=forms.TextInput(attrs={'class': 'form-control'}))
