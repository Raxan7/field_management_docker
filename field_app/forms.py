from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()
from field_app.models import CustomUser 
from .models import LogbookEntry
from .models import StudentTeacher
# field_app/forms.py

from django import forms
from .models import Assessor, School

class AssessorLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
class DocumentUploadForm(forms.Form):
    file = forms.FileField()

# Custom login form using email instead of username
class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'academic-input w-full pl-10 pr-3 py-3 rounded-lg',
            'placeholder': 'student@university.edu',
            'id': 'email'
        }),
        label='University Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'academic-input w-full pl-10 pr-10 py-3 rounded-lg',
            'placeholder': '••••••••',
            'id': 'password'
        }),
        label='Password'
    )


class StudentRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, label="Full Name")
    phone_number = forms.CharField(max_length=15, label="Phone Number")

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'full_name', 'phone_number')  # hizi mbili za mwisho si field za model moja kwa moja

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Optional if username not used
        if commit:
            user.save()
            StudentTeacher.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user


class LogbookForm(forms.ModelForm):
    class Meta:
        model = LogbookEntry
        fields = [
            'morning_activity', 
            'afternoon_activity', 
            'challenges_faced', 
            'lessons_learned'
        ]
        widgets = {
            'morning_activity': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Shughuli za asubuhi...',
                'class': 'form-control'
            }),
            'afternoon_activity': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Shughuli za mchana...',
                'class': 'form-control'
            }),
            'challenges_faced': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Changamoto ulizokutana nazo...',
                'class': 'form-control'
            }),
            'lessons_learned': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Mafunzo uliyoyapata...',
                'class': 'form-control'
            }),
        }
        labels = {
            'morning_activity': 'Shughuli za Asubuhi',
            'afternoon_activity': 'Shughuli za Mchana',
            'challenges_faced': 'Changamoto',
            'lessons_learned': 'Mafunzo',
        }

class StudentTeacherForm(forms.ModelForm):
    class Meta:
        model = StudentTeacher
        fields = '__all__'
# forms.py


class RegionFieldInputForm(forms.Form):
    academic_year = forms.CharField(label="Academic Year (e.g. 2025/2026)")
    allowed_regions = forms.CharField(
        label="Regions for Field (comma-separated)",
        widget=forms.TextInput(attrs={'placeholder': 'Dodoma, Singida'})
    )
# forms.py

# field_app/forms.py - ONGEZA HII


# field_app/forms.
# forms.py - UPDATE BulkAssignForm

class BulkAssignForm(forms.Form):
    assessors = forms.ModelMultipleChoiceField(
        queryset=Assessor.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2-multiple'}),
        required=True,
        label="Select Assessors"
    )
    
    schools = forms.ModelMultipleChoiceField(
        queryset=School.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2-multiple'}),
        required=True,
        label="Select Schools"
    )
    
    assessment_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Assessment Date"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        assessors = cleaned_data.get('assessors', [])
        
        # Check each assessor has email
        for assessor in assessors:
            if not assessor.email:
                raise forms.ValidationError(
                    f"Assessor '{assessor.full_name}' doesn't have an email. "
                    f"Please add email in admin panel first."
                )
        
        return cleaned_data
