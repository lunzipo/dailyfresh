from django.db import models


class BaseModel(models.Model):
    '''模型类抽象基类'''
    is_delete = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True  # 说明这个类是一个抽象类。迁移生成表的时候，不会生成数据库

