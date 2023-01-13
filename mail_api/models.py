from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
import pytz

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

STATUS = (
    ('future', 'future'),
    ('active', 'active'),
    ('paused', 'paused'),
    ('outdated', 'outdated')
)


class Mail(models.Model):
    start_at = models.DateTimeField(verbose_name="Старт")
    text = models.TextField(max_length=1000, verbose_name="Текст")
    clients = models.ManyToManyField('Client', blank=True, verbose_name="Клиенты")
    stop_at = models.DateTimeField(verbose_name="Стоп")
    status = models.CharField(max_length=20, default=STATUS[0][0], blank=True, null=True, choices=STATUS, verbose_name='Статус')
    schedule = models.CharField(max_length=30,
                                help_text="* * * * * (Minute, Hour, Day_of_Month, Month, Day_of_Week",
                                null=True, blank=True, verbose_name='Расписание')
    time_gap_start = models.TimeField(blank=True, null=True, verbose_name="Начало периода")
    time_gap_end = models.TimeField(blank=True, null=True, verbose_name="Окончание периода")

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-stop_at']


class Client(models.Model):
    mobile = models.CharField(max_length=11, validators=[MinLengthValidator(11), MaxLengthValidator(11)],
                              help_text="7XXXXXXXXXX", verbose_name="Номер телефона")
    operator = models.IntegerField(blank=True, verbose_name="Оператор")
    timezone = models.CharField(max_length=32, choices=TIMEZONES, verbose_name="Часовой пояс")
    tag = models.ManyToManyField('Tag', blank=True, verbose_name="Тэг")
    tag_list = models.TextField(max_length=200, blank=True, null=True, verbose_name="Список тэгов")

    def save(self, *args, **kwargs):
        self.operator = int(self.mobile[1:4])
        super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.mobile)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['id']

    def tags(self):
        return "\n".join([t.name + ',' for t in self.tag.all()])


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name="Тэг")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']


class Message(models.Model):
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_status = models.BooleanField(default=True, verbose_name="Статус")
    mail = models.ForeignKey('Mail', on_delete=models.CASCADE, related_name="messages", verbose_name="Рассылка")
    receiver = models.ForeignKey('Client', null=True, on_delete=models.PROTECT, verbose_name="Клиенты")

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-id']
