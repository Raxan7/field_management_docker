from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth import get_user_model  # 🔥 ONGEZA HII
# models.py
# 🔥 ONGEZA HII
# =========================
# Custom User
# =========================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# =========================
# Student Profile
# =========================

class StudentTeacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    selected_school = models.ForeignKey('School', null=True, blank=True, on_delete=models.SET_NULL)
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS_CHOICES, default='pending')

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='approved_students',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    subjects = models.ManyToManyField('Subject', blank=True)

    def __str__(self):
        return self.full_name

# =========================
# Geography
# =========================

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.region.name})"

# =========================
# School & Subjects
# =========================

class School(models.Model):
    SCHOOL_LEVEL_CHOICES = [
        ('Primary', 'Primary School'),
        ('Secondary', 'Secondary School'),
    ]

    name = models.CharField(max_length=200)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    level = models.CharField(max_length=10, choices=SCHOOL_LEVEL_CHOICES)
    capacity = models.PositiveIntegerField(default=10)
    current_students = models.PositiveIntegerField(default=0)
    
    # 🔥 ONGEZA FIELDS HIZI KWA LOCATION
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"

class Subject(models.Model):
    LEVEL_CHOICES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='secondary')

    def __str__(self):
        return f"{self.name} ({self.level})"

class SchoolSubjectCapacity(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    max_students = models.PositiveIntegerField(default=2)
    current_students = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('school', 'subject')

    def __str__(self):
        return f"{self.school.name} - {self.subject.name}"

# =========================
# Academic Year & Pinning
# =========================

class AcademicYear(models.Model):
    year = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.year

# =========================
# Problematic Schools Model - ONGEZA HII
# =========================

class ProblematicSchool(models.Model):
    PROBLEM_CHOICES = [
        ('no_electricity', 'Hakuna Umeme'),
        ('water_issues', 'Matatizo ya Maji'),
        ('headmaster_refusal', 'Mkuu wa Shule Hakubali'),
        ('infrastructure', 'Matatizo ya Miundombinu'),
        ('security', 'Matatizo ya Usalama'),
        ('other', 'Nyingine'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    problem_type = models.CharField(max_length=50, choices=PROBLEM_CHOICES)
    description = models.TextField(help_text="Maelezo ya kina kuhusu shida")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='resolved_schools', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['academic_year', 'school']
        verbose_name_plural = "Problematic Schools"
    
    def __str__(self):
        return f"{self.school.name} - {self.get_problem_type_display()}"

class RegionPin(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    is_pinned = models.BooleanField(default=True)

    class Meta:
        unique_together = ('academic_year', 'region')

class SchoolPin(models.Model):
    PIN_REASON_CHOICES = [
        ('manual', 'Manual Pin'),
        ('problematic', 'Shule Yenye Shida'),
        ('capacity', 'Ujazo Kamili'),
        ('other', 'Nyingine'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    is_pinned = models.BooleanField(default=True)
    pin_reason = models.CharField(max_length=20, choices=PIN_REASON_CHOICES, default='manual')
    problem_details = models.ForeignKey(
        ProblematicSchool, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='school_pins'
    )
    pinned_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    pinned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('academic_year', 'school')

    def __str__(self):
        return f"{self.school.name} - {self.get_pin_reason_display()}"

# =========================
# Logbook (REKEBISHWA - ONDOA GIS)
# =========================

class LogbookEntry(models.Model):
    DAY_CHOICES = [
        ('monday', 'Jumatatu'),
        ('tuesday', 'Jumanne'),
        ('wednesday', 'Jumatano'),
        ('thursday', 'Alhamisi'),
        ('friday', 'Ijumaa'),
    ]
    
    student = models.ForeignKey(StudentTeacher, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    
    # Activity fields
    morning_activity = models.TextField(blank=True, null=True)
    afternoon_activity = models.TextField(blank=True, null=True)
    challenges_faced = models.TextField(blank=True, null=True)
    lessons_learned = models.TextField(blank=True, null=True)
    
    # Location verification
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    location_address = models.CharField(max_length=255, blank=True, null=True)
    is_location_verified = models.BooleanField(default=False)
    
    # School verification
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    is_at_school = models.BooleanField(default=False)
    
    # Timestamps
    morning_check_in = models.DateTimeField(blank=True, null=True)
    afternoon_check_out = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.date}"
    
    def save(self, *args, **kwargs):
        # Auto-set day of week based on date
        if self.date:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            self.day_of_week = days[self.date.weekday()]
        
        # Auto-set school from student's selected school
        if not self.school and self.student.selected_school:
            self.school = self.student.selected_school
            
        super().save(*args, **kwargs)

# =========================
# Approval Letters
# =========================

class ApprovalLetter(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    students = models.ManyToManyField(StudentTeacher)
    generated_date = models.DateTimeField(auto_now_add=True)
    letter_file = models.FileField(upload_to='approval_letters/')

    def __str__(self):
        return f"Approval Letter for {self.school.name}"

# =========================
# School Requirements
# =========================

class SchoolRequirement(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    year = models.IntegerField()
    required_students = models.IntegerField()

# =========================
# File Uploads
# =========================

class SchoolUpdateFile(models.Model):
    file = models.FileField(upload_to='uploads/school_updates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update file {self.file.name} uploaded at {self.uploaded_at}"

# =========================
# Student Applications
# =========================

class StudentApplication(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(StudentTeacher, on_delete=models.CASCADE, related_name='applications')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=APPLICATION_STATUS_CHOICES, 
        default='pending'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='approved_applications',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'subject', 'school')
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} at {self.school.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Hakikisha application ina student na school
        if not self.student_id:
            raise ValueError("Application must have a student")
        if not self.school_id:
            raise ValueError("Application must have a school")
        super().save(*args, **kwargs)

# =========================
# 🔥 ASSESSOR MODELS - FIXED: Use settings.AUTH_USER_MODEL
# =========================




# =========================
# 🔥 ASSESSOR MODELS - FIXED
# =========================

# field_app/models.py - ADD SCHOOL FIELD TO ASSESSOR
# field_app/models.py - REMOVE EMAIL FIELD

# field_app/models.py

# models.py - UPDATE ASSESSOR MODEL

class Assessor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, blank=True, null=True)  # ✅ ADD THIS
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    credentials_sent = models.BooleanField(default=False)  # ✅ Track credentials
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def save(self, *args, **kwargs):
        # Only create user if doesn't exist
        if not self.user and self.email:
            try:
                User = get_user_model()
                
                # Check if user already exists with this email
                existing_user = User.objects.filter(email=self.email).first()
                
                if existing_user:
                    # Link to existing user
                    self.user = existing_user
                    print(f"✅ Linked assessor {self.full_name} to existing user: {self.email}")
                else:
                    # Create new user with random password
                    import random
                    import string
                    
                    # Generate random password
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                    
                    # Create user
                    user = User.objects.create_user(
                        email=self.email,
                        password=password,
                        is_staff=False,
                        is_active=True
                    )
                    self.user = user
                    print(f"✅ Created user for assessor: {self.full_name}")
                    print(f"📧 Email: {self.email}")
                    print(f"🔑 Password: {password}")
                    
            except Exception as e:
                print(f"❌ Error creating user for assessor {self.full_name}: {e}")
        
        super().save(*args, **kwargs)
    
    def get_login_credentials(self):
        """Return credentials if user exists"""
        if self.user:
            return {
                'email': self.email,
                'username': self.user.username,
                'has_password': True,
            }
        return None
class SchoolAssessment(models.Model):
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE)
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    assessment_date = models.DateField(default=timezone.now)  # 🔥 SAHIHI: timezone.now (bila mabano)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['assessor', 'school']
    
    def __str__(self):
        return f"{self.assessor} - {self.school}"

class StudentAssessment(models.Model):
    ASSESSMENT_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE)
    student = models.ForeignKey('StudentTeacher', on_delete=models.CASCADE)
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    assessment_date = models.DateField(default=timezone.now)  # 🔥 SAHIHI: timezone.now (bila mabano)
    status = models.CharField(max_length=20, choices=ASSESSMENT_STATUS, default='pending')
    score = models.CharField(max_length=10, blank=True, default='')
    comments = models.TextField(blank=True, default='')
    
    def __str__(self):
        return f"{self.assessor} - {self.student}"
