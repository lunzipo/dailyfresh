# 定义任务函数
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/6')


@app.task
def send_active_email(token, username, email):
    '''发送激活邮件'''
    subject = '天天生鲜用户激活'  # 标题
    message = ''
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [email]  # 收件人列表
    html_message = "<a href='http://127.0.0.1:8000/user/active/%s/'>尊敬的%s，请点击激活帐号。激活链接（1小时内有效）</a>" % \
                   (token, username)

    send_mail(subject, message, sender, receiver, html_message=html_message)
