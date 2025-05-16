"""

Developed By : Tech Norte Soluções
Instagram : norte_dev



"""




from django.contrib import admin
from django.urls import path, include
from hospital import views
from django.contrib.auth.views import LoginView,LogoutView
from django.conf.urls import handler403
from hospital.views import (
    # Unidades de Saúde
    lista_unidades,
    unidade_novo,
    unidade_update,
    # Escalas
    PdfEscalas,
    lista_escalas,
    escala_novo,
    escala_update,
    escala_delete,
    # Folgas
    lista_folgas,
    PdfFolgas,
    folga_novo,
    folga_update,
    folga_delete,
    # Controle Medicamentos
    medicines_page,
    add_medicine_page,
    update_medicine,
    delete_medicine,
    use_medicine,
    medicine_report,
    
    ####### ADICIONANDO ROOM e ROOMHISTORY
    
    lista_quartos,
    detalhe_quarto,
    historico_quartos
    
)


handler403 = 'django.views.defaults.permission_denied'

#-------------FOR ADMIN RELATED URLS
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name='home'),
    path('api/', include('api.urls')),  # Inclua as URLs do aplicativo
    


    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),


    path('adminclick', views.adminclick_view),
    path('doctorclick', views.doctorclick_view),
    path('patientclick', views.patientclick_view),
    path('nurseclick', views.nurseclick_view),

    path('adminsignup', views.admin_signup_view),
    path('doctorsignup', views.doctor_signup_view,name='doctorsignup'),
    path('nursesignup', views.nurse_signup_view, name='nursesignup'),
    path('patientsignup', views.patient_signup_view),
    
    
    ############ ADICIONANDO ERRO LOGIN USUARIO NAO CADASTRADO ####################
    path('adminlogin', LoginView.as_view(template_name='hospital/adminlogin.html'), name='adminlogin'),
    path('doctorlogin', LoginView.as_view(template_name='hospital/doctorlogin.html'), name='doctorlogin'),
    path('patientlogin', LoginView.as_view(template_name='hospital/patientlogin.html'), name='patientlogin'),
    path('nurselogin', LoginView.as_view(template_name='hospital/nurselogin.html'), name='nurselogin'),

    
    
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout', LogoutView.as_view(template_name='hospital/index.html'),name='logout'),


    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('admin-doctor', views.admin_doctor_view,name='admin-doctor'),
    path('admin-view-doctor', views.admin_view_doctor_view,name='admin-view-doctor'),
    path('delete-doctor-from-hospital/<int:pk>', views.delete_doctor_from_hospital_view,name='delete-doctor-from-hospital'),
    path('update-doctor/<int:pk>', views.update_doctor_view,name='update-doctor'),
    path('admin-add-doctor', views.admin_add_doctor_view,name='admin-add-doctor'),
    path('admin-approve-doctor', views.admin_approve_doctor_view,name='admin-approve-doctor'),
    path('approve-doctor/<int:pk>', views.approve_doctor_view,name='approve-doctor'),
    path('reject-doctor/<int:pk>', views.reject_doctor_view,name='reject-doctor'),
    path('admin-view-doctor-specialisation',views.admin_view_doctor_specialisation_view,name='admin-view-doctor-specialisation'),


    path('admin-patient', views.admin_patient_view,name='admin-patient'),
    path('admin-view-patient', views.admin_view_patient_view,name='admin-view-patient'),
    path('delete-patient-from-hospital/<int:pk>', views.delete_patient_from_hospital_view,name='delete-patient-from-hospital'),
    path('update-patient/<int:pk>', views.update_patient_view,name='update-patient'),
    path('admin-add-patient', views.admin_add_patient_view,name='admin-add-patient'),
    path('admin-approve-patient', views.admin_approve_patient_view,name='admin-approve-patient'),
    path('approve-patient/<int:pk>', views.approve_patient_view,name='approve-patient'),
    path('reject-patient/<int:pk>', views.reject_patient_view,name='reject-patient'),
    path('admin-discharge-patient', views.admin_discharge_patient_view,name='admin-discharge-patient'),
    path('discharge-patient/<int:pk>', views.discharge_patient_view,name='discharge-patient'),
    path('download-pdf/<int:pk>', views.download_pdf_view,name='download-pdf'),


    path('admin-appointment', views.admin_appointment_view,name='admin-appointment'),
    path('admin-view-appointment', views.admin_view_appointment_view,name='admin-view-appointment'),
    path('admin-add-appointment', views.admin_add_appointment_view,name='admin-add-appointment'),
    path('admin-approve-appointment', views.admin_approve_appointment_view,name='admin-approve-appointment'),
    path('approve-appointment/<int:pk>', views.approve_appointment_view,name='approve-appointment'),
    path('reject-appointment/<int:pk>', views.reject_appointment_view,name='reject-appointment'),
]


#---------FOR NURSE RELATED URLS-------------------------------------
urlpatterns +=[
    path('nurse-dashboard', views.nurse_dashboard_view,name='nurse-dashboard'),
    path('search', views.search_view,name='search'),

    path('doctor-patient', views.nurse_patient_view,name='nurse-patient'),
    path('nurse-view-patient', views.nurse_view_patient_view,name='nurse-view-patient'),
    path('nurse-view-discharge-patient',views.nurse_view_discharge_patient_view,name='nurse-view-discharge-patient'),

    path('nurse-appointment', views.nurse_appointment_view,name='nurse-appointment'),
    path('nurse-view-appointment', views.nurse_view_appointment_view,name='nurse-view-appointment'),
    path('nurse-delete-appointment',views.nurse_delete_appointment_view,name='nurse-delete-appointment'),
    path('delete-appointment/<int:pk>', views.delete_appointment_view,name='delete-appointment'),
    # Nova rota para designar um médico via nurse
    path('assign-doctor/<int:patient_id>', views.assign_doctor_to_patient_view, name='assign-doctor'),
    
    #  Rota para nurse adicionar paciente
    path('nurse-add-patient', views.nurse_add_patient_view, name='nurse-add-patient'),

    #  Rota para nurse adicionar appointment
    path('nurse-add-appointment', views.nurse_add_appointment_view, name='nurse-add-appointment'),

    #  Rota para nurse aprovar appointments pendentes
    path('nurse-approve-appointment', views.nurse_approve_appointment_view, name='nurse-approve-appointment'),
]




#---------FOR DOCTOR RELATED URLS-------------------------------------
urlpatterns +=[
    path('doctor-dashboard', views.doctor_dashboard_view,name='doctor-dashboard'),
    path('search', views.search_view,name='search'),

    path('doctor-patient', views.doctor_patient_view,name='doctor-patient'),
    path('doctor-view-patient', views.doctor_view_patient_view,name='doctor-view-patient'),
    path('doctor-view-discharge-patient',views.doctor_view_discharge_patient_view,name='doctor-view-discharge-patient'),

    path('doctor-appointment', views.doctor_appointment_view,name='doctor-appointment'),
    path('doctor-view-appointment', views.doctor_view_appointment_view,name='doctor-view-appointment'),
    path('doctor-delete-appointment',views.doctor_delete_appointment_view,name='doctor-delete-appointment'),
    path('delete-appointment/<int:pk>', views.delete_appointment_view,name='delete-appointment'),
]




#---------FOR PATIENT RELATED URLS-------------------------------------
urlpatterns +=[

    path('patient-dashboard', views.patient_dashboard_view,name='patient-dashboard'),
    path('patient-appointment', views.patient_appointment_view,name='patient-appointment'),
    path('patient-book-appointment', views.patient_book_appointment_view,name='patient-book-appointment'),
    path('patient-view-appointment', views.patient_view_appointment_view,name='patient-view-appointment'),
    path('patient-view-doctor', views.patient_view_doctor_view,name='patient-view-doctor'),
    path('searchdoctor', views.search_doctor_view,name='searchdoctor'),
    path('patient-discharge', views.patient_discharge_view,name='patient-discharge'),



######################################################################################
######################################################################################
####################### ESCALAS, ROOM, ROOMHISTORY ###################################

    # Postos / Unidades
    path('unidades', lista_unidades, name='hospital_lista_unidades'),
    path('unidade-novo', unidade_novo, name='hospital_unidade_novo'),
    path('unidade-update/<int:id>/', unidade_update, name='hospital_unidade_update'),

    # Escalas
    path('escalas', lista_escalas, name='hospital_lista_escalas'),
    path('escala-novo', escala_novo, name='hospital_escala_novo'),
    path('escala-update/<int:id>/', escala_update, name='hospital_escala_update'),
    path('escala-delete/<int:id>/', escala_delete, name='hospital_escala_delete'),
    path('relatorio-pdf/', PdfEscalas.as_view(), name='relatorio_pdf_escalas'),

    ###### Folgas #####
    path('folgas', lista_folgas, name='hospital_lista_folgas'),
    path('folga-novo', folga_novo, name='hospital_folga_novo'),
    path('folga-update/<int:id>/', folga_update, name='hospital_folga_update'),
    path('folga-delete/<int:id>/', folga_delete, name='hospital_folga_delete'),
    path('relatorio-folgas-pdf/', PdfFolgas.as_view(), name='relatorio_pdf_folgas'),

######################## ROOM, ROOMHISTORY ####################################


# Rooms # 
  path('quartos/', views.lista_quartos, name='hospital_lista_quartos'),
  path('quarto/<int:id>/', views.detalhe_quarto, name='hospital_detalhe_quarto'),
  path('quartos/historico/', views.historico_quartos, name='hospital_historico_quartos'),


############################ MEDICINE URLS CRUD ##########################################

  # Medicine CRUD
  path('medicines/', medicines_page, name="view-medicines"),
  path('medicines/add-medicine/', add_medicine_page, name="add-medicine"),
  path('medicines/update-medicine/<int:pk>/', update_medicine, name="update-medicine"),
  path('medicines/delete-medicine/<int:pk>/', delete_medicine, name="delete-medicine"),
  path('medicines/use/', use_medicine, name="use-medicine"),
  path('medicines/relatorio/', medicine_report, name='relatorio-remedios'),

]


#Developed By : Tech Norte Soluções
#Instagram: norte_dev
