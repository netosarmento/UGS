from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
import datetime
from django.utils import timezone

# Constante global para departamentos
DEPARTMENTS = [
    ('Cardiologista', 'Cardiologista'),
    ('Dermatologista', 'Dermatologista'),
    ('Clinico Geral', 'Clinico Geral'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergistas/Immunologistas', 'Allergistas/Immunologistas'),
    ('Anestesiologistas', 'Anestesiologistas'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons')
]

ROOM_TYPES = [
    ('UTI', 'UTI'),
    ('CTI', 'CTI'),
    ('Emergência', 'Emergência'),
    ('Enfermaria', 'Enfermaria'),
    ('Isolamento', 'Isolamento'),
    ('Sala de Observação', 'Sala de Observação'),
]



class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)  # Aguardando aprovação

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.user.first_name} ({'Aprovado' if self.status else 'Pendente'})"




class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, default='Cardiologista')
    status = models.BooleanField(default=False)
    available = models.BooleanField(default=False)

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
    numero_cns = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d{15}$', message='O número do CNS deve conter 15 dígitos.')],
        verbose_name="Número do CNS",
        help_text="Informe os 15 dígitos do Cartão Nacional de Saúde",
        null=True,
        blank=True
    )
    mobile = models.CharField(max_length=20)
    symptoms = models.CharField(max_length=100)
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    admit_date = models.DateField(default=timezone.now)
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
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


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
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/NurseProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, default='Clinico Geral')
    status = models.BooleanField(default=False)
    available = models.BooleanField(default=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return f"{self.user.first_name} ({self.department})"
 ######################################################################################### 
 ################# MEDICINE MODELS #######################################################
 #########################################################################################  
 
class Medicine(models.Model):
    med_code = models.IntegerField(unique=True)  # unique para tornar único o código
    med_name = models.CharField(max_length=50)
    lab = models.CharField(max_length=100)       # ✅ adicione max_length para evitar erro
    stock = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.med_code}: {self.med_name}"

    def get_update_url(self):
        return reverse('update-medicine', args=[self.id])  # ✅ rota que exige pk

    def get_delete_url(self):
        return reverse('delete-medicine', args=[self.id])  # ✅ rota que exige pk



class MedicineUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    

    def save(self, *args, **kwargs):
        # Atualiza o estoque
        if self.medicine.stock >= self.quantity:
            self.medicine.stock -= self.quantity
            self.medicine.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Quantidade solicitada maior que o estoque disponível.")
        
    def __str__(self):
       return f"{self.user.username} usou {self.quantity} de {self.medicine.med_name}"

################## RELATORIO ############################################################
class MedicineLog(models.Model):
    ACTION_CHOICES = [
        ('ADD', 'Adição'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Remoção'),
        ('USE', 'Uso em paciente'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.get_action_display()} - {self.medicine.med_name} por {self.user.username}"







##########################################################################################
class Unidade(models.Model):
    nome = models.CharField(max_length=50)
    rua = models.CharField(max_length=50)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=20)
    cidade = models.CharField(max_length=30)
    disponivel = models.BooleanField(default=True)

    class Meta:
        unique_together = ['nome', 'rua', 'numero']

    def __str__(self):
        return self.nome


class Folga(models.Model):
    data = models.DateField()
    medico = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    enfermeiro = models.ForeignKey(Nurse, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        # Validação de exclusividade
        if self.medico and self.enfermeiro:
            raise ValidationError("Selecione apenas médico OU enfermeiro — não ambos.")
        if not self.medico and not self.enfermeiro:
            raise ValidationError("Você deve selecionar um médico ou um enfermeiro.")

        # Se for médico, validar se já tem escala
        if self.medico:
            if Escala.objects.filter(data=self.data, medico=self.medico).exists():
                raise ValidationError(f"O médico {self.medico} já está escalado para o dia {self.data.strftime('%d/%m/%Y')}.")

        # Se for enfermeiro, validar se já tem escala
        if self.enfermeiro:
            if Escala.objects.filter(data=self.data, enfermeiro=self.enfermeiro).exists():
                raise ValidationError(f"O enfermeiro {self.enfermeiro} já está escalado para o dia {self.data.strftime('%d/%m/%Y')}.")

    def save(self, *args, **kwargs):
        self.full_clean()  # isso chama o clean automaticamente
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data} - Médico: {self.medico or '---'} - Enfermeiro: {self.enfermeiro or '---'}"


class Escala(models.Model):
    data = models.DateField(null=True)
    local = models.ForeignKey('Unidade', on_delete=models.SET_NULL, null=True)
    medico = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    enfermeiro = models.ForeignKey('Nurse', on_delete=models.SET_NULL, null=True, blank=True)
    disponivel = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['data', 'medico'], name='unique_escala_medico'),
            models.UniqueConstraint(fields=['data', 'enfermeiro'], name='unique_escala_enfermeiro'),
        ]

    def clean(self):
        # Verifica se ambos estão preenchidos ou ambos vazios
        if self.medico and self.enfermeiro:
            raise ValidationError("Você deve selecionar apenas médico OU enfermeiro — não ambos.")
        
        if not self.medico and not self.enfermeiro:
            raise ValidationError("Você deve selecionar um médico ou um enfermeiro.")

        # Valida folgas
        if self.medico and Folga.objects.filter(data=self.data, medico=self.medico).exists():
            raise ValidationError(f"O médico {self.medico} está de folga no dia {self.data.strftime('%d/%m/%Y')}.")

        if self.enfermeiro and Folga.objects.filter(data=self.data, enfermeiro=self.enfermeiro).exists():
            raise ValidationError(f"O enfermeiro {self.enfermeiro} está de folga no dia {self.data.strftime('%d/%m/%Y')}.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Garante que clean() seja chamado
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data} - Unidade: {self.local} - Médico: {self.medico or '---'} - Enfermeiro: {self.enfermeiro or '---'}"



class Room(models.Model):
    numero = models.CharField(max_length=10)
    tipo = models.CharField(max_length=30, choices=ROOM_TYPES)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    paciente = models.ForeignKey("Patient", on_delete=models.SET_NULL, null=True, blank=True)
    entrada = models.DateTimeField(null=True, blank=True, editable=False)
    saida = models.DateTimeField(null=True, blank=True, editable=False)
    disponivel = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['numero', 'unidade']

    def __str__(self):
        ocupado = f" - Ocupado por: {self.paciente.get_name}" if self.paciente else " - Disponível"
        return f"Quarto {self.numero} ({self.tipo}) - {self.unidade.nome}{ocupado}"

    def save(self, *args, **kwargs):
        agora = timezone.now()
        novo_paciente = self.paciente
        quarto_antigo = Room.objects.filter(pk=self.pk).first() if self.pk else None
        paciente_anterior = quarto_antigo.paciente if quarto_antigo else None

        # Verifica se está tentando trocar paciente enquanto o quarto ainda está ocupado
        if paciente_anterior and paciente_anterior != novo_paciente and not self.saida:
            raise ValidationError("Este quarto já está ocupado. Libere-o antes de atribuir um novo paciente.")

        if novo_paciente:
            if not self.entrada or self.saida:
                self.entrada = agora
                self.saida = None
            self.disponivel = False
        else:
            if not self.saida:
                self.saida = agora
            self.entrada = None
            self.disponivel = True

        super().save(*args, **kwargs)

        # Atualiza histórico
        if novo_paciente and (not paciente_anterior or paciente_anterior != novo_paciente):
            RoomHistory.objects.create(room=self, paciente=novo_paciente, entrada=self.entrada)
        elif not novo_paciente:
            RoomHistory.objects.filter(room=self, saida__isnull=True).update(saida=self.saida)


            
            
class RoomHistory(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    paciente = models.ForeignKey("Patient", on_delete=models.SET_NULL, null=True)
    entrada = models.DateTimeField()
    saida = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        nome = self.paciente.get_name if self.paciente else 'Paciente removido'
        entrada_str = self.entrada.strftime('%d/%m/%Y %H:%M')
        saida_str = self.saida.strftime('%d/%m/%Y %H:%M') if self.saida else '---'
        return f"{nome} em {self.room} de {entrada_str} até {saida_str}"






#Developed By : Neto Sarmento
#Instagram: nort_dev
#Geral: Tech Norte Soluções
