from django.shortcuts import render,redirect,reverse, get_object_or_404
from . import forms,models
from django.db.models import Sum
from .models import Room, RoomHistory
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, FileResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date, timezone
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import logout
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.core.exceptions import ValidationError
import io
from django.views import View
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .forms import(
    UnidadeForm,
    FolgaForm,
    EscalaForm,
    AddMedicineForm,
    UpdateMedicineForm,
    MedicineUsageForm
)
from .models import (
    Unidade,
    Folga,
    Escala,
    Medicine,
    MedicineUsage,
    MedicineLog,
    Patient,
    Doctor,
    Nurse,
)

# ERRO USUARIO NAO LOGADO

def erro_403(request, exception=None):
    return render(request, '403.html', status=403)

# Criando as views de logout GERAL

def logout_view(request):
    logout(request)
    return redirect('home')  # home_view deve estar registrada com name='home'




# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/index.html')


#for showing signup/login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')


#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')

#for showing signup/login button for Nurse(by sumit)
def nurseclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/nurseclick.html')


def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
        
    return render(request,'hospital/adminsignup.html',{'form':form})




def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'hospital/doctorsignup.html',context=mydict)

# Adding Nurse
def nurse_signup_view(request):
    userForm=forms.NurseUserForm()
    nurseForm=forms.NurseForm()
    mydict={'userForm':userForm,'nurseForm':nurseForm}
    if request.method=='POST':
        userForm=forms.NurseUserForm(request.POST)
        nurseForm=forms.NurseForm(request.POST,request.FILES)
        if userForm.is_valid() and nurseForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            nurse=nurseForm.save(commit=False)
            nurse.user=user
            nurse=nurse.save()
            my_nurse_group = Group.objects.get_or_create(name='NURSE')
            my_nurse_group[0].user_set.add(user)
        return HttpResponseRedirect('nurselogin')
    return render(request,'hospital/nursesignup.html',context=mydict)



def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}

    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)

        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            patient = patientForm.save(commit=False)
            patient.user = user

            has_doctor = request.POST.get('has_doctor')
            if has_doctor == 'yes':
                assignedDoctorId = request.POST.get('assignedDoctorId')
                if assignedDoctorId:
                    patient.assigned_doctor_id = int(assignedDoctorId) #adicionando paciente ao medico se tiver
            else:
                patient.assigned_doctor = None

            patient.save() #salvando paciente 

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

            return HttpResponseRedirect('patientlogin')

        else:
            print("UserForm errors:", userForm.errors)
            print("PatientForm errors:", patientForm.errors)

    return render(request, 'hospital/patientsignup.html', context=mydict)






#-----------for checking user is doctor , patient or admin(by sumit)
def is_admin(user):
    if user.groups.filter(name='ADMIN').exists():
             return True
    raise PermissionDenied
def is_doctor(user):
    if user.groups.filter(name='DOCTOR').exists():
        return True
    raise PermissionDenied
def is_patient(user):
    if user.groups.filter(name='PATIENT').exists():
        return True
    raise PermissionDenied
#Adding nurse
def is_nurse(user):
    if user.groups.filter(name='NURSE').exists():
        return True
    raise PermissionDenied


# CONTROL MEDICINE

def is_admin_or_staff(user):
    if user.groups.filter(name__in=['ADMIN', 'DOCTOR', 'NURSE']).exists():
        return True
    raise PermissionDenied


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
@login_required
def afterlogin_view(request):
    if is_admin(request.user) or request.user.is_superuser:
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval = models.Doctor.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor_wait_for_approval.html')
    elif is_nurse(request.user):
        accountapproval = models.Doctor.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('nurse-dashboard')
        else:
            return render(request, 'hospital/nurse_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval = models.Patient.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request, 'hospital/patient_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')  # ou mostre uma página de erro amigável
###################################################################################
##################  ADD MEDICINE VIEWS ############################################
###################################################################################


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def medicines_page(request):
    medicines = Medicine.objects.all().order_by('med_name')

    context = {
        "medicines": medicines
    }
    return render(request, "hospital/view-medicines.html", context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin_or_staff)
def add_medicine_page(request):
    form = AddMedicineForm()

    if request.method == "POST":
        form = AddMedicineForm(request.POST)
        if form.is_valid():
            med_code = form.cleaned_data.get("med_code")
            med_name = form.cleaned_data.get("med_name")
            lab = form.cleaned_data.get("lab")
            stock = form.cleaned_data.get("stock")
            description = form.cleaned_data.get("description")

            medicine = Medicine(
                med_code=med_code, med_name=med_name, lab=lab,
                stock=stock, description=description
            )
            medicine.save()
            messages.success(request, "Você adicionou novo medicamento ao estoque.")
            return redirect("view-medicines")
        return redirect("add-medicine")

    context = {
        "form": form
    }
    return render(request, "hospital/add-medicine.html", context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_medicine(request, pk):
    medicine = get_object_or_404(Medicine, id=pk)
    form = UpdateMedicineForm(instance=medicine)

    if request.method == "POST":
        form = UpdateMedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, "Você Atualizou o estoque de medicamentos.")
            return redirect("view-medicines")
        return redirect("update-medicine")

    context = {
        "form": form,
    }
    return render(request, "hospital/update-medicine.html", context)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_medicine(request, pk):
    medicine = get_object_or_404(Medicine, id=pk)
    medicine.delete()
    messages.success(request, "Você deletou com sucesso, medicamento do estoque.")
    return redirect("view-medicines")


@login_required(login_url='adminlogin')
@user_passes_test(is_admin_or_staff)
def use_medicine(request):
    form = MedicineUsageForm()
    if request.method == "POST":
        form = MedicineUsageForm(request.POST)
        if form.is_valid():
            usage = form.save(commit=False)
            usage.user = request.user

            if usage.quantity > usage.medicine.stock:
                messages.error(request, "Quantidade excede o estoque disponível.")
            else:
                try:
                    usage.save()

                    # Atualiza o estoque do medicamento
                    usage.medicine.stock -= usage.quantity
                    usage.medicine.save()

                    # Cria o log de uso do medicamento
                    MedicineLog.objects.create(
                        user=request.user,
                        medicine=usage.medicine,
                        action='USE',
                        quantity=usage.quantity,
                        patient=usage.patient if hasattr(usage, 'patient') else None,
                        notes=usage.notes
                    )

                    messages.success(request, "Medicamento utilizado com sucesso.")
                except ValueError as e:
                    messages.error(request, str(e))

            return redirect("view-medicines")

    return render(request, "hospital/usage-medicine.html", {"form": form})


@login_required
@user_passes_test(is_admin_or_staff)
def medicine_report(request):
    logs = MedicineLog.objects.select_related('medicine', 'user', 'patient').all()

    # Filtros
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    medicine_id = request.GET.get('medicine')
    patient_id = request.GET.get('patient')

    if start_date:
        logs = logs.filter(timestamp__date__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__date__lte=end_date)
    if medicine_id:
        logs = logs.filter(medicine_id=medicine_id)
    if patient_id:
        logs = logs.filter(patient_id=patient_id)

    # PDF dos últimos 30 dias
    if request.GET.get('pdf') == '1':
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Relatório de Uso de Medicamentos - Últimos 30 dias", styles["Heading2"]))

        data = [["Data", "Medicamento", "Ação", "Usuário", "Quantidade", "Paciente", "Notas"]]
        last_30_days = timezone.now() - timedelta(days=30)
        logs_pdf = logs.filter(timestamp__gte=last_30_days)

        for log in logs_pdf:
            data.append([
                log.timestamp.strftime("%d/%m/%Y %H:%M"),
                log.medicine.med_name,
                log.get_action_display(),
                log.user.username,
                log.quantity,
                log.patient.full_name if log.patient else "-",
                log.notes or "-"
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="relatorio_medicamentos.pdf")

    context = {
        "logs": logs,
        "medicines": Medicine.objects.all(),
        "patients": Patient.objects.all(),
    }
    return render(request, "hospital/relatorio_remedios.html", context)






#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
# view do admin login
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # Pegando médicos e adicionando o campo tipo manualmente
    doctors = models.Doctor.objects.all().order_by('-id')
    nurses = models.Nurse.objects.all().order_by('-id')

    profissionais = []

    for doc in doctors:
        doc.tipo = 'Médico'  # Sobrescreve ou cria dinamicamente
        profissionais.append(doc)

    for nur in nurses:
        nur.tipo = 'Enfermeiro'
        profissionais.append(nur)

    # Pacientes
    patients = models.Patient.objects.all().order_by('-id')

    # Contagens
    doctorcount = models.Doctor.objects.filter(status=True).count()
    pendingdoctorcount = models.Doctor.objects.filter(status=False).count()

    nursecount = models.Nurse.objects.filter(status=True).count()
    pendingnursecount = models.Nurse.objects.filter(status=False).count()

    patientcount = models.Patient.objects.filter(status=True).count()
    pendingpatientcount = models.Patient.objects.filter(status=False).count()

    appointmentcount = models.Appointment.objects.filter(status=True).count()
    pendingappointmentcount = models.Appointment.objects.filter(status=False).count()

    context = {
        'profissionais': profissionais,
        'patients': patients,
        'nursecount': nursecount,
        'pendingnursecount': pendingnursecount,
        'doctorcount': doctorcount,
        'pendingdoctorcount': pendingdoctorcount,
        'patientcount': patientcount,
        'pendingpatientcount': pendingpatientcount,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
    }

    return render(request, 'hospital/admin_dashboard.html', context)



# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})

# Verificar necessidade adicionar nurse



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'hospital/admin_update_doctor.html',context=mydict)



# achar add-medico #
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor_specialisation.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'hospital/admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'hospital/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'hospital/admin_discharge_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    days=(date.today()-patient.admitDate) #2 days, 0:00:00
    assignedDoctor=models.User.objects.all().filter(id=patient.assignedDoctorId)
    d=days.days # only how many day that is 2
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        #for updating to database patientDischargeDetails (pDD)
        pDD=models.PatientDischargeDetails()
        pDD.patientId=pk
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'hospital/patient_final_bill.html',context=patientDict)
    return render(request,'hospital/patient_generate_bill.html',context=patientDict)



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'hospital/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#------------------------ ESCALA RELATED VIEWS BEGIN ------------------------------
#---------------------------------------------------------------------------------






# ---------- PDF RELATÓRIOS ----------
# ---------- PDF RELATÓRIOS ----------

class PdfEscalas(View):                 
    def get(self, request):           
        escalas = Escala.objects.all()  
        params = {
            'escalas': escalas,
            'request': request,
        }
        return Render.render('hospital/relatorio_escalas.html', params, 'relatorio-escalas')


class Render:
    @staticmethod
    def render(path: str, params: dict, filename: str): 
        template = get_template(path)
        html = template.render(params)
        response = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), response)

        if not pdf.err:
            response = HttpResponse(response.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment;filename={filename}.pdf'
            return response
        else:
            return HttpResponse("Erro ao gerar PDF", status=400)


# ---------- FOLGAS ----------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def lista_folgas(request):
    form = FolgaForm()
    folgas = Folga.objects.all()
    return render(request, 'hospital/lista_folgas.html', {
        'form': form,
        'folgas': folgas
    })

###### AQUI FOLGA NOVO ######

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def folga_novo(request):
    form = FolgaForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
                sucesso = 'Folga cadastrada com sucesso!'
                return render(request, 'hospital/lista_folgas.html', {
                    'form': FolgaForm(),  # limpa o form
                    'folgas': Folga.objects.all(),
                    'sucesso': sucesso
                })
            except ValidationError as e:
                erro = "; ".join(e.messages)
        else:
            erro = "Preencha todos os campos corretamente."

        return render(request, 'hospital/lista_folgas.html', {
            'form': form,
            'folgas': Folga.objects.all(),
            'erro': erro
        })

    return render(request, 'hospital/lista_folgas.html', {
        'form': form,
        'folgas': Folga.objects.all()
    })
######### RELATORIO DE FOLGAS ########


class PdfFolgas(View):                 
    def get(self, request):           
        folgas = Folga.objects.all()  
        params = {
            'folgas': folgas,
            'request': request,
        }
        return Render.render('hospital/relatorio_folgas.html', params, 'relatorio-folgas')


######################################
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def folga_update(request, id):
    folga = get_object_or_404(Folga, id=id)
    form = FolgaForm(request.POST or None, instance=folga)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('hospital_lista_folgas')

    return render(request, 'hospital/update_folgas.html', {'form': form, 'folga': folga})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def folga_delete(request, id):
    folga = get_object_or_404(Folga, id=id)
    if request.method == 'POST':
        folga.delete()
        return redirect('hospital_lista_folgas')
    return render(request, 'hospital/delete_confirm.html', {'obj': folga})

# ---------- ESCALAS ----------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def lista_escalas(request):
    escalas = Escala.objects.filter(disponivel=True)
    form = EscalaForm()
    return render(request, 'hospital/lista_escalas.html', {'escalas': escalas, 'form': form})

##### AJUSTANDO PARA BOTAR A ESCALA #######


##### ESCALA NOVO #####
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def escala_novo(request):
    form = EscalaForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
                sucesso = 'Escala cadastrada com sucesso!'
                return render(request, 'hospital/lista_escalas.html', {
                    'form': EscalaForm(),
                    'escalas': Escala.objects.filter(disponivel=True),
                    'sucesso': sucesso
                })
            except ValidationError as e:
                erro = "; ".join(e.messages)
        else:
            erro = "Preencha todos os campos corretamente."

        return render(request, 'hospital/lista_escalas.html', {
            'form': form,
            'escalas': Escala.objects.filter(disponivel=True),
            'erro': erro
        })

    # GET: exibir a página normalmente
    escalas = Escala.objects.filter(disponivel=True)
    return render(request, 'hospital/lista_escalas.html', {
        'form': form,
        'escalas': escalas
    })



#############################################
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def escala_update(request, id):
    escala = Escala.objects.get(id=id)
    form = EscalaForm(request.POST or None, instance=escala)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('hospital_lista_escalas')

    return render(request, 'hospital/update_escala.html', {'form': form, 'escala': escala})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def escala_delete(request, id):
    escala = Escala.objects.get(id=id)
    if request.method == 'POST':
        escala.delete()
        return redirect('hospital_lista_escalas')
    return render(request, 'hospital/delete_confirm2.html', {'obj': escala})


# ---------- POSTOS / UNIDADES ----------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def lista_unidades(request):
    unidades = Unidade.objects.filter(disponivel=True)
    form = UnidadeForm()
    return render(request, 'hospital/lista_unidades.html', {'unidades': unidades, 'form': form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def unidade_novo(request):
    form = UnidadeForm(request.POST or None)
    if form.is_valid():
        form.save()
        sucesso = 'Unidade de Saúde cadastrada com sucesso!'
        unidades = Unidade.objects.filter(disponivel=True)
        return render(request, 'hospital/lista_unidades.html', {'unidades': unidades, 'form': UnidadeForm(), 'sucesso': sucesso})
    return redirect('hospital_lista_unidades')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def unidade_update(request, id):
    unidade = get_object_or_404(Unidade, id=id)
    form = UnidadeForm(request.POST or None, instance=unidade)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('hospital_lista_unidades')

    return render(request, 'hospital/update_unidade.html', {'form': form, 'unidade': unidade})






#############################################################################

############################################################################
###############################################################################
##################################################################################
################# ROOM, ROOMHISTORY ########################################



# Lista de quartos
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def lista_quartos(request):
    quartos = Room.objects.select_related('paciente__assigned_doctor').all()
    return render(request, 'hospital/lista_quartos.html', {'quartos': quartos})

# Detalhe de um quarto
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def detalhe_quarto(request, id):
    quarto = get_object_or_404(Room, id=id)
    return render(request, 'hospital/detalhe_quarto.html', {'quarto': quarto})

# Histórico de quartos
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def historico_quartos(request):
    historico = RoomHistory.objects.select_related('paciente', 'room').all()
    return render(request, 'hospital/historico_quartos.html', {'historico': historico})















#---------------------------------------------------------------------------------
#------------------------ ESCALA RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------


#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_patient.html',context=mydict)





@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------
##################################################################################
# Adicionando os nurses aqui 

@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count() #parei aqui
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/nurse_dashboard.html',context=mydict)



@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/nurse_patient.html',context=mydict)





@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/nurse_view_patient.html',{'patients':patients,'doctor':doctor})


@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_view_discharge_patient_view(request):
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/nurse_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})



@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/nurse_appointment.html',{'doctor':doctor})



@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/nurse_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/nurse_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/nurse_delete_appointment.html',{'appointments':appointments,'doctor':doctor})


@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def assign_doctor_to_patient_view(request, patient_id):
    nurse = models.Nurse.objects.get(user=request.user)
    patient = get_object_or_404(models.Patient.objects.get(id=patient_id))

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        if doctor_id:
            patient.assignedDoctorId = int(doctor_id)
            patient.save()
            return redirect('nurse-view-patient')  # Redirecionando nurse para view do patient

    # lista todos os médicos disponíveis
    doctors = models.Doctor.objects.filter(status=True)

    return render(request, 'hospital/nurse_assign_doctor.html', {
        'patient': patient,
        'doctors': doctors,
        'nurse': nurse,
    })

# Adicionando o nurse aprovando paciente e aprovando a appointment
@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('nurse-view-appointment')
    return render(request,'hospital/nurse_add_appointment.html',context=mydict)



@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/nurse_approve_appointment.html',{'appointments':appointments})

@login_required(login_url='nurselogin')
@user_passes_test(is_nurse)
def nurse_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('nurse-view-patient')
    return render(request,'hospital/nurse_add_patient.html',context=mydict)








# NURSERING
#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor=models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict={
    'patient':patient,
    'doctorName':doctor.get_name,
    'doctorMobile':doctor.mobile,
    'doctorAddress':doctor.address,
    'symptoms':patient.symptoms,
    'doctorDepartment':doctor.department,
    'admitDate':patient.admitDate,
    }
    return render(request,'hospital/patient_dashboard.html',context=mydict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm=forms.PatientAppointmentForm()
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            desc=request.POST.get('description')

            doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request,'hospital/patient_book_appointment.html',context=mydict)



def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})



def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'hospital/patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'hospital/patient_discharge.html',context=patientDict)


#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form':sub})


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------



#Developed By : Neto Sarmento
#Instagram : norte_dev
#Geral : Tech Norte Soluções
