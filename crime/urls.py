from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import api_views

urlpatterns = [
    path('', views.introduction, name='intro'),  # root shows introduction
    path('home/', views.index, name='home'),
    path('login/', views.login_view, name='login'),  # fixed path & view
    path('signup/', views.signup_view, name='signup'),
    path('course/', views.course, name='course'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('trend/',views.trend_view,name='trend'),
    path('insights/',views.insights,name='insights'),
    path('activity-dashboard/', views.activity_dashboard, name='activity_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('about/',views.about_page, name='about'),

    path(
    'api/skills/demand/',
    api_views.skill_demand_api,
    name='skill-demand-api'
),
   path(
    'api/jobs/',
    api_views.job_list_api,
    name='job-list-api'
),

   path('jobs/', views.jobs_page, name='jobs'),

   path('jobs/<int:job_id>/', views.job_detail, name='job-detail'),
]


