from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^admin/resetdevice/?$', views.reset_device, name='admin_reset_device'),
    url(r'^admin/setdevice/?$', views.set_device_params, name='admin_set_device'),
    url(r'^admin/gettemp/?$', views.get_device_temp, name='admin_get_temp'),
    url(r'^admin/monitor/?$', views.monitor_experiment, name='admin_monitor'),
]
