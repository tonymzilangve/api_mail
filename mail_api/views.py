from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .pagination import CustomPageNumberPagination
from .serializers import *
from .models import Mail
from .tasks import send_mail_task
import json


class MailViewSet(viewsets.ModelViewSet):
    queryset = Mail.objects.all().order_by('-stop_at')    # status
    serializer_class = MailSerializer

    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['id', 'status']
    search_fields = ['id', 'clients__mobile', 'text', 'status']
    ordering_fields = ['id', 'start_at', 'stop_at', 'status', 'clients__count']

    def create(self, request, *args, **kwargs):
        """ Создание и запуск рассылки """

        serializer = MailSerializer(data=request.data)
        if serializer.is_valid():
            mail_id = serializer.validated_data["id"]
            start = serializer.validated_data['start_at']
            stop = serializer.validated_data['stop_at']
            schedule = serializer.validated_data['schedule'].split(' ')
            serializer.save()

            if len(schedule) == 5:
                minute = schedule[0]
                hour = schedule[1]
                day_of_month = schedule[2]
                month = schedule[3]
                day_of_week = schedule[4]

                cron_schedule, created = CrontabSchedule.objects.get_or_create(
                    minute=minute,
                    hour=hour,
                    day_of_month=day_of_month,
                    month_of_year=month,
                    day_of_week=day_of_week,
                )

                task = PeriodicTask.objects.create(
                    crontab=cron_schedule,
                    name=f'ID: {mail_id} - cron: {cron_schedule}',
                    task='send_mail_task',
                    start_time=start,
                    expires=stop,
                    args=(mail_id,)
                )
                print("Периодическая рассылка запущена!")

            else:
                send_mail_task.delay(mail_id)
                print("Рассылка успешно выполнена!")

            return Response({'status': 'Mail created'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        try:
            instance = Mail.objects.get(pk=pk)
        except:
            return Response({'error': 'Данной рассылки не существует!'})

        serializer = MailSerializer(data=request.data, instance=instance)
        if serializer.is_valid():
            mail_id = serializer.validated_data["id"]
            start = serializer.validated_data.get('start_at', instance.start_at)
            stop = serializer.validated_data.get('stop_at', instance.start_at)
            schedule = serializer.validated_data.get('schedule', instance.schedule).split(' ')
            serializer.save()

            tasks = PeriodicTask.objects.filter(name__icontains=f"ID: {pk}")
            if tasks:
                for task in tasks:
                    task.delete()

            if len(schedule) == 5:
                minute = schedule[0]
                hour = schedule[1]
                day_of_month = schedule[2]
                month = schedule[3]
                day_of_week = schedule[4]

                cron_schedule, created = CrontabSchedule.objects.get_or_create(
                    minute=minute,
                    hour=hour,
                    day_of_month=day_of_month,
                    month_of_year=month,
                    day_of_week=day_of_week,
                )

                task = PeriodicTask.objects.create(
                    crontab=cron_schedule,
                    name=f'ID: {mail_id} - cron: {cron_schedule}',
                    task='send_mail_task',
                    start_time=start,
                    expires=stop,
                    args=(mail_id,)
                )
                print("Периодическая рассылка запущена!")

            else:
                send_mail_task.delay(mail_id)
                print("Рассылка успешно выполнена!")

            return Response({'status': 'Mail updated!'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            tasks = PeriodicTask.objects.filter(name__icontains=f"ID: {pk}")
            for task in tasks:
                task.delete()

            mail = Mail.objects.get(pk=pk)
            mail.delete()
        except:
            return Response({'error': 'Данной рассылки не существует'})

        return Response({'status': 'Mail deleted!'})


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['id', 'operator', 'timezone', 'tag']
    search_fields = ['id', 'mobile', 'operator', 'timezone', 'tag']
    ordering_fields = ['id', 'mobile', 'operator', 'timezone']

    def create(self, request, *args, **kwargs):
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid():
            tags = serializer.validated_data.get('tag_list', None)
            if tags:
                tags = tags.split(', ')
                serializer.save()

                new_client = Client.objects.all().order_by('-id').first()
                for t in tags:
                    tag = Tag.objects.get_or_create(name=t)[0]
                    if not tag in new_client.tag.all():
                        new_client.tag.add(tag)
                return Response(serializer.data)

            serializer.save()
            return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid():
            tags = serializer.validated_data.get('tag_list', None)
            if tags:
                tags = tags.split(', ')
                serializer.save()

                try:
                    updated_client = Client.objects.get(pk=pk)
                except:
                    return Response({"error": "Данного клиента не существует!"})

                for t in tags:
                    tag = Tag.objects.get_or_create(name=t)[0]
                    if not tag in updated_client.tag.all():
                        updated_client.tag.add(tag)

                for t in updated_client.tag.all():
                    if t.name not in tags:
                        updated_client.tag.remove(name=t.name)

                return Response(serializer.data)

        serializer.save()
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticated,)


class MessageAPIView(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticated,)


class StatisticsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):

        if pk:
            payload = {
                "mail_id": pk,
                "all_sent_mail": Message.objects.filter(mail=pk).count(),
                "client_count": Mail.objects.get(pk=pk).clients.count()
            }

        else:
            payload = {
                "total_mail": Mail.objects.all().count(),
                "active_mail": Mail.objects.filter(status="active").count(),
                "total_msg": Message.objects.all().count(),
                "total_clients": Client.objects.all().count()
            }

        return Response(payload)


