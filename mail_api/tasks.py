import json
import os

from django.template import Engine, Context
from django.utils import timezone
from celery import shared_task

import requests
import smtplib

from email.mime.text import MIMEText
from email.utils import formatdate

from mail_api.models import Mail, Message, Client, STATUS


def render_template(template, context):
    engine = Engine.get_default()
    tmpl = engine.get_template(template)
    return tmpl.render(Context(context))


@shared_task(bind=True, name="send_mail_task")
def send_mail_task(request, mail_id, *args, **kwargs):

    try:
        mail = Mail.objects.get(id=mail_id)
    except Exception as e:
        return f"{e}\nТакой рассылки не существует!"

    if mail.time_gap_start <= timezone.now().time() <= mail.time_gap_end:
        token = os.getenv('EXTERNAL_API_TOKEN')

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        for client in mail.clients.all():
            msg = Message.objects.create(mail=mail, receiver=client)

            payload = {
                'id': msg.id,
                'phone': int(client.mobile),
                'text': mail.text
            }

            res = requests.post(f'{os.getenv("EXTERNAL_URL")}/{msg.id}', headers=headers, data=json.dumps(payload))
            print(res.status_code)

            if res.status_code != 200:
                msg.sent_status = False
                print(res.json(), '\nСообщение не отправлено!')
            else:
                print(res.json(), '\nОчередное сообщение отправлено!')

        return "Рассылка завершена!"


@shared_task(bind=True, name="check_mail_status")
def check_mail_status(request, *args, **kwargs):
    mails = Mail.objects.all()

    if mails:
        for mail in mails:
            if timezone.now() > mail.stop_at:
                mail.status = STATUS[3][0]
                # mail.status = "outdated"
            else:
                if timezone.now() > mail.start_at:
                    mail.status = STATUS[1][0]
                else:
                    mail.status = STATUS[0][0]
    else:
        return "Не создана ни одна рассылка."

    return "Статусы рассылок успешно обновлены"


@shared_task(bind=True, name="send_statistics")
def send_statistics(request, *args, **kwargs):
    """ Send statistics to email everyday at 09:00 """

    server = smtplib.SMTP(os.getenv('EMAIL_HOST'), os.getenv('EMAIL_PORT'))
    server.starttls()

    try:
        server.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
    except Exception as e:
        return f"{e}\nПроверьте данные отправителя!"

    email = os.getenv("STAT_EMAIL")

    context = {
        "total_mail": Mail.objects.all(),
        "active_mail": Mail.objects.filter(status="active"),
        "other_mail": Mail.objects.exclude(status="active"),
        "total_msg": Message.objects.all(),
        "total_clients": Client.objects.all(),
    }

    msg = MIMEText(render_template('stat.html', context), "html")
    msg['From'] = os.getenv('EMAIL_HOST_USER')
    msg['To'] = email
    msg['Date'] = formatdate(localtime=True)
    msg["Subject"] = "Статистика По Рассылкам"
    msg['X-Confirm-Reading-To'] = os.getenv('EMAIL_HOST_USER')
    server.sendmail(os.getenv('EMAIL_HOST_USER'), email, msg.as_string(), rcpt_options=['NOTIFY=SUCCESS,DELAY,FAILURE'])

    server.quit()
    return "Сводки по статистике были успешно отправлены на почту."

