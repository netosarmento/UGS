from django.db import models
from django.contrib.auth.models import User
import datetime

# Constante global para departamentos
DEPARTMENTS = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Clinico Geral', 'Clinico Geral'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons')
]

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, default='Cardiologist')
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.user.first_name} ({self.department})"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    numero_cns = models.CharField(max_length=15, null=True, blank=True)
    mobile = models.CharField(max_length=20)
    symptoms = models.CharField(max_length=100)
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    admit_date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id
    
    @property
    def assignedDoctorId(self):
        return self.assigned_doctor.id if self.assigned_doctor else None

    def __str__(self):
        return f"{self.user.first_name} ({self.symptoms})"


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    patient_name = models.CharField(max_length=40, null=True)
    doctor_name = models.CharField(max_length=40, null=True)
    appointment_date = models.DateField(auto_now_add=True)
    description = models.TextField(max_length=500)
    status = models.BooleanField(default=False)


class PatientDischargeDetails(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    patient_name = models.CharField(max_length=40)
    numero_cns = models.CharField(max_length=15, null=True, blank=True)
    assigned_doctor_name = models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    symptoms = models.CharField(max_length=100, null=True)

    admit_date = models.DateField()
    release_date = models.DateField(default=datetime.date.today)
    day_spent = models.PositiveIntegerField()

    room_charge = models.PositiveIntegerField()
    medicine_cost = models.PositiveIntegerField()
    doctor_fee = models.PositiveIntegerField()
    other_charge = models.PositiveIntegerField()
    total = models.PositiveIntegerField()


class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/NurseProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, default='Clinico Geral')
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.user.first_name} ({self.department})"



#Developed By : Neto Sarmento
#Instagram: nort_dev
#Geral: Tech Norte Soluções
