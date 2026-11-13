 
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls', namespace='accounts')),
    path('api/v1/organizations/', include('apps.organizations.urls', namespace='organizations')),
    path('api/v1/facilities/', include('apps.facilities.urls', namespace='facilities')),
    path('api/v1/patients/', include('apps.patients.urls', namespace='patients')),
    path('api/v1/patient-reports/', include('apps.patients.report_urls', namespace='patient-reports')),
    path('api/v1/reports/', include('apps.reporting.urls', namespace='reporting')),
    path('api/v1/sync/', include('apps.synchronization.urls', namespace='synchronization')),
    path('api/v1/audit/', include('apps.audit.urls', namespace='audit')),
]
