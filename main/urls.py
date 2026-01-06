from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('', views.home, name='homepage'),
                  path('stats/', views.stats, name='statistics'),
                  path('job_demand/', views.job_demand, name='job_demand'),
                  path('regions/', views.regions, name='regions'),
                  path('skills_overview/', views.skills_overview, name='skills_overview'),
                  path('recent_jobs/', views.recent_jobs, name='recent_jobs'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
