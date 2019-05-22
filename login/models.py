from django.db import models
from .cpabe import PairingGroup,CPabe_sheme
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair,serialize,deserialize

attrs=['ONE','TWO','THREE','FOUR'];
groupObj = PairingGroup('SS512')
cpabe = CPabe_sheme(groupObj)
    
class User(models.Model):


    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    attr=models.CharField(max_length=1024)
    K=models.TextField()
    K0=models.TextField()
    K_x=models.TextField()

    def __str__(self):
        return self.name
    def __key__(self):
        d=dict()
        data=self.K_x.split()
        attr_list=self.attr.strip().split(',')
        for i in range(0,len(attr_list)):
            d[attr_list[i]]=groupObj.deserialize(bytes(data[i],encoding='utf-8'))

        return {
            'K':groupObj.deserialize(bytes(self.K,encoding='utf-8')),
            'K0':groupObj.deserialize(bytes(self.K0,encoding='utf-8')),
            'K_x':d,
            'attributes':attr_list
        }
    class Meta:
        ordering = ["name"]
        verbose_name = "用户"
        verbose_name_plural = "用户"

