from django.db import models
from .cpabe import PairingGroup, CPabe_sheme
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, serialize, deserialize

attrs = ['医疗部', '门诊部', '住院部', '医务部', '护理部', '住院部', '院长']
groupObj = PairingGroup('SS512')
cpabe = CPabe_sheme(groupObj)


class User(models.Model):

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    attr = models.CharField(max_length=1024)
    K = models.TextField()
    K0 = models.TextField()
    K_x = models.TextField()

    def __str__(self):
        return self.name

    def __key__(self):
        d = dict()
        data = self.K_x.split()
        attr_list = self.attr.strip().split(',')
        for i in range(0, len(attr_list)):
            d[attr_list[i]] = groupObj.deserialize(
                bytes(data[i], encoding='utf-8'))

        return {
            'K': groupObj.deserialize(bytes(self.K, encoding='utf-8')),
            'K0': groupObj.deserialize(bytes(self.K0, encoding='utf-8')),
            'K_x': d,
            'attributes': attr_list
        }

    class Meta:
        ordering = ["name"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


class Record(models.Model):
    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    rid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    sex = models.CharField(max_length=32, choices=gender, default='男')
    age = models.IntegerField(default=0)
    idcard = models.CharField(unique=True, max_length=128)
    attr = models.CharField(max_length=1024)
    time = models.DateTimeField(auto_now_add=True)
    detail = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["rid"]
        verbose_name = "医疗记录"
        verbose_name_plural = "医疗记录"
