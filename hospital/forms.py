from django import forms
from django.contrib.auth.models import User
from . import models
from .models import (
    Unidade,
    Folga,
    Escala,
    RoomHistory,
    Room,
    Medicine,
    MedicineUsage
)


# Admin signup
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("A senha deve ter pelo menos 6 caracteres.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# Doctor
class DoctorUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("A senha deve ter pelo menos 6 caracteres.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class DoctorForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['address', 'mobile', 'department', 'status', 'profile_pic']


# Patient
class PatientUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("A senha deve ter pelo menos 6 caracteres.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class PatientForm(forms.ModelForm):
    assigned_doctor = forms.ModelChoiceField(
        queryset=models.Doctor.objects.all().filter(status=True),
        empty_label="Nome e Departamento",
        to_field_name="user_id",
        required=False
    )

    class Meta:
        model = models.Patient
        fields = ['address', 'mobile', 'status', 'symptoms', 'profile_pic']


class AppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(
        queryset=models.Doctor.objects.all().filter(status=True),
        empty_label="Médico Nome e Departmento",
        to_field_name="user_id"
    )
    patientId = forms.ModelChoiceField(
        queryset=models.Patient.objects.all().filter(status=True),
        empty_label="Paciente Nome e Sintomas",
        to_field_name="user_id"
    )

    class Meta:
        model = models.Appointment
        fields = ['description', 'status']


class PatientAppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(
        queryset=models.Doctor.objects.all().filter(status=True),
        empty_label="Médico Nome e Departmento",
        to_field_name="user_id"
    )

    class Meta:
        model = models.Appointment
        fields = ['description', 'status']


# Contact Us
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 30})
    )


# Nurse
class NurseUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("A senha deve ter pelo menos 6 caracteres.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class NurseForm(forms.ModelForm):
    class Meta:
        model = models.Nurse
        fields = ['address', 'mobile', 'department', 'status', 'profile_pic']


class UnidadeForm(forms.ModelForm):
    class Meta:
        model = Unidade
        fields = '__all__'
        
        
        
###############################################################
############# ADD MEDICINE ####################################
class AddMedicineForm(forms.ModelForm):
    
    class Meta:
        model = Medicine
        fields = [
            "med_code", "med_name", "lab",
             "stock", "description"
        ]
        widgets = {
            'med_code': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'validationMedCode',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                }
            ),
            'med_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'validationMedName',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                }
            ),
            'lab': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'validationMedName',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                }
            ),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'validationStock',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                'type': "number"
                }
            ),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                }
            ),
        }


class UpdateMedicineForm(forms.ModelForm):
    
    class Meta:
        model = Medicine
        fields = [
            "med_code", "med_name", "lab",
            "stock", "description"
        ]
        widgets = {
            'med_code': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'validationMedCode',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                }
            ),
            'med_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'validationMedName',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                }
            ),
            'lab': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'validationMedName',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                }
            ),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'validationStock',
                'aria-describedby': 'inputGroupPrepend',
                'required': "true",
                'type': "number"
                }
            ),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                }
            ),
        }


class MedicineUsageForm(forms.ModelForm):
    class Meta:
        model = MedicineUsage
        fields = ['medicine', 'quantity', 'patient', 'notes']  # Adicionando "patient"

        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'patient': forms.Select(attrs={'class': 'form-control'}),  # o paciente que foi utilizado
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }




########################################################################

class FolgaForm(forms.ModelForm):
    class Meta:
        model = Folga
        fields = ['data', 'medico', 'enfermeiro']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'enfermeiro': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        medico = cleaned_data.get('medico')
        enfermeiro = cleaned_data.get('enfermeiro')

        if medico and enfermeiro:
            raise forms.ValidationError("Selecione apenas um: médico OU enfermeiro.")
        if not medico and not enfermeiro:
            raise forms.ValidationError("É necessário selecionar um médico OU um enfermeiro.")

        return cleaned_data


class EscalaForm(forms.ModelForm):
    class Meta:
        model = Escala
        fields = ['data', 'local', 'medico', 'enfermeiro', 'disponivel']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        medico = cleaned_data.get('medico')
        enfermeiro = cleaned_data.get('enfermeiro')

        if medico and enfermeiro:
            raise forms.ValidationError("Escolha apenas um: médico OU enfermeiro.")

        if not medico and not enfermeiro:
            raise forms.ValidationError("Você precisa selecionar um médico ou um enfermeiro.")


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['created_at', 'updated_at']


class RoomHistoryForm(forms.ModelForm):
    class Meta:
        model = RoomHistory
        exclude = ['criado_em']


#Developed By : Neto Sarmento
#Instagram : norte_dev
#Geral: Tech Norte Soluções
