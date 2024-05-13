from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.DashboardView.as_view(), name='dashboard'),
    path('competence/', views.EmployeeCompetenceView.as_view(), name='employee-competence'),
    path('competence/<int:employee_id>', views.EmployeeCompetenceView.as_view(), name='employee-competence-update'),
    path('aboutme/<int:pk>/', views.EmployeeAboutMeUpdateView.as_view(), name='employee-update'),
    path('belbintest/', views.EmployeeBelbinTest.as_view(), name='employee-belbin-test'),

    path('project/', views.ProjectView.as_view(), name='project-list'),
    path('project/add', views.ProjectCreateView.as_view(), name='project-create'),
    path('project/<int:pk>', views.ProjectUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/delete', views.ProjectDeleteView.as_view(), name='project-delete'),

    path('employee/', views.EmployerEmployeesView.as_view(), name='employee-list'),
]
