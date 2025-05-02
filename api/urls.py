# Developed: Neto Sarmento
#Instagram: nort_dev

from django.urls import path
from .views import CNSView, buscar_cns_view, dados_cidadao_view
from . import views

urlpatterns = [
    path('cns/<str:cns>/', CNSView.as_view(), name='buscar-cns'),
    path('buscar-cns/', views.buscar_cns_view, name='buscar-cns'),
    path('dados-paciente/', views.dados_cidadao_view, name='dados-cidadao'),
]
