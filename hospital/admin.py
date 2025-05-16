from django.contrib import admin
from .models import (
    Doctor, Patient, Appointment, PatientDischargeDetails,
    Nurse, Unidade, Folga, Escala, Room, RoomHistory, Medicine, MedicineUsage
)



class MedicineAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'med_code', 'med_name', 'lab',
        'stock', 'description'
    ]
    
admin.site.register(Medicine, MedicineAdmin)
admin.site.register(MedicineUsage)



# Doctor Admin
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'department', 'mobile', 'status', 'available')
    list_filter = ('department', 'status', 'available')
    search_fields = ('user__first_name', 'user__last_name', 'department')

# Patient Admin
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'numero_cns', 'mobile', 'admit_date', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'numero_cns', 'symptoms')
    list_filter = ('status', 'admit_date')

# Appointment Admin
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor_name', 'appointment_date', 'status')
    search_fields = ('patient_name', 'doctor_name')
    list_filter = ('appointment_date', 'status')

# Discharge Admin
@admin.register(PatientDischargeDetails)
class PatientDischargeDetailsAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'assigned_doctor_name', 'release_date', 'total')
    search_fields = ('patient_name', 'assigned_doctor_name', 'numero_cns')
    list_filter = ('release_date',)

# Nurse Admin
@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'department', 'mobile', 'status', 'available')
    list_filter = ('department', 'status', 'available')
    search_fields = ('user__first_name', 'user__last_name', 'department')

# Unidade Admin
@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'rua', 'numero', 'bairro', 'cidade', 'disponivel')
    search_fields = ('nome', 'bairro', 'cidade')
    list_filter = ('cidade', 'disponivel')

# Folga Admin
@admin.register(Folga)
class FolgaAdmin(admin.ModelAdmin):
    list_display = ('data', 'medico', 'enfermeiro')
    search_fields = ('medico__user__first_name', 'enfermeiro__user__first_name')
    list_filter = ('data',)

# Escala Admin
@admin.register(Escala)
class EscalaAdmin(admin.ModelAdmin):
    list_display = ('data', 'local', 'medico', 'enfermeiro', 'disponivel')
    search_fields = ('medico__user__first_name', 'enfermeiro__user__first_name', 'local__nome')
    list_filter = ('data', 'disponivel')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'unidade', 'paciente', 'entrada', 'saida', 'disponivel')
    list_filter = ('tipo', 'unidade', 'disponivel')
    search_fields = ('numero', 'unidade__nome', 'paciente__user__first_name')

@admin.register(RoomHistory)
class RoomHistoryAdmin(admin.ModelAdmin):
    list_display = ('room', 'paciente', 'entrada', 'saida')
    list_filter = ('room__tipo', 'entrada', 'saida')
    search_fields = ('paciente__user__first_name', 'room__numero')


#Developed By : Neto Sarmento
#Instagram: norte_dev
#Geral: Tech Norte Soluções