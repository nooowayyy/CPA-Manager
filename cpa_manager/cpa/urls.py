from django.conf import settings
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "cpa"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("campanhas/", views.campaign_list, name="campaign_list"),
    path("campanhas/nova/", views.campaign_create, name="campaign_create"),
    path("campanhas/<int:pk>/editar/", views.campaign_edit, name="campaign_edit"),
    path("campanhas/<int:pk>/excluir/", views.campaign_delete, name="campaign_delete"),
    path("desempenho/", views.record_list, name="record_list"),
    path("desempenho/novo/", views.record_create, name="record_create"),
    path("desempenho/<int:pk>/editar/", views.record_edit, name="record_edit"),
    path("desempenho/<int:pk>/excluir/", views.record_delete, name="record_delete"),
    path("importacoes/", views.import_view, name="import_data"),
    path("integracoes/", views.integration_settings, name="integration_settings"),
    path("relatorios/exportar/", views.export_csv, name="export_csv"),
    path("api/v1/metrics/", views.api_metrics, name="api_metrics"),
]

# Cadastro aberto é necessário apenas no pacote independente. Ao incorporar o
# app em um projeto principal, o padrão é reutilizar o cadastro central.
if getattr(settings, "CPA_ENABLE_REGISTRATION", False):
    urlpatterns.insert(1, path("cadastro/", views.register, name="register"))
