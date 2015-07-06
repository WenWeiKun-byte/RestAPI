"""joieAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from authentication import views as av
from jobs import views as jv


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'employers', av.EmployerViewSet)
router.register(r'employees', av.EmployeeViewSet)
router.register(r'industry', av.IndustryViewSet)
router.register(r'joblisttype', jv.JobListTypeViewSet)
router.register(r'job_draft', jv.DraftJobViewSet, base_name='job_draft')
router.register(r'job_active', jv.ActiveJobViewSet, base_name='job')


urlpatterns = [
    url(r'^auth/me/$', av.UserView.as_view(), name='user'),
    url(r'^auth/create/admin/$', av.StaffRegistrationView.as_view(), name='admin_create'),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/frontend/(?P<uid>[a-zA-Z0-9]+)/(?P<token>[a-zA-Z0-9-]+)', av.activate),
    url(r'^auth/reset/(?P<uid>[a-zA-Z0-9]+)/(?P<token>[a-zA-Z0-9-]+)', av.ResetConfirmView.as_view()),
    url(r'^', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

