from django.urls import path, include
from rest_framework import routers

from .views import *


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'mail', MailViewSet)
router.register(r'client', ClientViewSet)
router.register(r'tag', TagViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('msg', MessageAPIView.as_view(), name="all-messages"),
    path('stat', StatisticsView.as_view(), name="all_mail_stat"),
    path('stat/<int:pk>', StatisticsView.as_view(), name="mail_stat"),
]