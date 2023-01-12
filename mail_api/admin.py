from django.contrib import admin
from .models import *


class MailAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'start_at', 'stop_at')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'operator', 'timezone', 'tags')
    list_display_links = ('id', 'mobile')
    search_fields = ('mobile', 'tags')
    list_filter = ('operator', 'timezone', 'tag')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'mail', 'sent_at', 'sent_status')
    list_display_links = ('id', 'mail')
    search_fields = ('mail', 'receiver')
    list_filter = ('mail', 'receiver', 'sent_status')


admin.site.register(Mail, MailAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Message, MessageAdmin)
