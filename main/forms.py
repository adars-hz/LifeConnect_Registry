from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, DonorProfile, RecipientProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with additional fields"""
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        required=True,
        widget=forms.RadioSelect,
        label='I am a'
    )
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    blood_group = forms.ChoiceField(
        choices=User.BLOOD_GROUPS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'user_type', 'phone', 'blood_group', 'date_of_birth', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class DonorRegistrationForm(forms.ModelForm):
    """Form for donor registration"""
    age = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '18', 'max': '100'}),
        help_text="Enter your age (18-100 years)"
    )
    gender = forms.ChoiceField(
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    organs_to_donate = forms.MultipleChoiceField(
        choices=User.ORGANS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
        required=True,
        help_text="Select all organs you are willing to donate"
    )
    medical_fitness_status = forms.ChoiceField(
        choices=[
            ('fit', 'Fit'),
            ('not_fit', 'Not Fit'),
        ],
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-control'})
    )
    medical_fitness_certificate = forms.FileField(
        required=False,  # Temporarily optional for testing
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload your medical fitness certificate (PDF, JPG, PNG)"
    )
    is_living_donor = forms.BooleanField(
        initial=True,
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    donation_after_death = forms.BooleanField(
        initial=True,
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    height = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text="Enter height in cm (e.g., 175.5)"
    )
    weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text="Enter weight in kg (e.g., 70.5)"
    )
    medications = forms.CharField(
        required=False,  # Only required if taking_medications is True
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'List your medications here...'}),
        help_text="List any medications you are currently taking"
    )
    taking_medications = forms.ChoiceField(
        choices=[
            ('no', 'No'),
            ('yes', 'Yes'),
        ],
        initial='no',
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-control'}),
        label="Are you currently taking any medications?"
    )
    consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I hereby declare that I am willing to donate organs voluntarily and have provided all true information to the best of my knowledge."
    )
    lab_reports = forms.FileField(
        required=False,  # Temporarily optional for testing
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload your lab reports (PDF, JPG, PNG)"
    )
    id_proof = forms.FileField(
        required=False,  # Temporarily optional for testing
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload your ID proof (Aadhar Card, Passport, Driver's License) - PDF, JPG, PNG"
    )
    
    class Meta:
        model = DonorProfile
        fields = ['age', 'gender', 'organs_to_donate', 'medical_fitness_status', 'medical_fitness_certificate', 
                  'is_living_donor', 'donation_after_death', 'height', 'weight', 'medications', 'taking_medications', 'lab_reports', 'id_proof', 'consent']
        widgets = {
            'organs_to_donate': forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and age < 18:
            raise forms.ValidationError("You must be at least 18 years old to register as a donor.")
        return age
    
    def clean_medications(self):
        medications = self.cleaned_data.get('medications', '')
        taking_medications = self.cleaned_data.get('taking_medications')
        
        if taking_medications == 'yes' and not medications.strip():
            raise forms.ValidationError("Please list the medications you are currently taking.")
        
        return medications
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        if user:
            # Add user fields as read-only
            self.fields['username'] = forms.CharField(
                initial=user.username,
                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
                label='Username',
                required=True
            )
            self.fields['email'] = forms.EmailField(
                initial=user.email,
                widget=forms.EmailInput(attrs={'class': 'form-control'}),
                label='Email',
                required=True
            )
            self.fields['first_name'] = forms.CharField(
                initial=user.first_name,
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='First Name',
                required=True
            )
            self.fields['last_name'] = forms.CharField(
                initial=user.last_name,
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='Last Name',
                required=True
            )
            self.fields['phone'] = forms.CharField(
                initial=user.phone,
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='Phone',
                required=True
            )
            self.fields['blood_group'] = forms.ChoiceField(
                choices=User.BLOOD_GROUPS,
                initial=user.blood_group,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Blood Group',
                required=True
            )
            self.fields['date_of_birth'] = forms.DateField(
                initial=user.date_of_birth,
                widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                label='Date of Birth',
                required=True
            )
            self.fields['address'] = forms.CharField(
                initial=user.address,
                widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                label='Address',
                required=True
            )
        else:
            # Add user fields for new user registration
            self.fields['username'] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='Username',
                required=True
            )
            self.fields['email'] = forms.EmailField(
                widget=forms.EmailInput(attrs={'class': 'form-control'}),
                label='Email',
                required=True
            )
            self.fields['password1'] = forms.CharField(
                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                label='Password',
                required=True
            )
            self.fields['password2'] = forms.CharField(
                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                label='Confirm Password',
                required=True
            )
            self.fields['first_name'] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='First Name',
                required=True
            )
            self.fields['last_name'] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='Last Name',
                required=True
            )
            self.fields['phone'] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='Phone',
                required=True
            )
            self.fields['blood_group'] = forms.ChoiceField(
                choices=User.BLOOD_GROUPS,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Blood Group',
                required=True
            )
            self.fields['date_of_birth'] = forms.DateField(
                widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                label='Date of Birth',
                required=True
            )
            self.fields['address'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                label='Address',
                required=True
            )
    
    def save(self, commit=True):
        # Update existing user instead of creating new one
        if self.user:
            # Update user fields from form data
            self.user.user_type = 'donor'
            if 'email' in self.cleaned_data:
                self.user.email = self.cleaned_data['email']
            if 'first_name' in self.cleaned_data:
                self.user.first_name = self.cleaned_data['first_name']
            if 'last_name' in self.cleaned_data:
                self.user.last_name = self.cleaned_data['last_name']
            if 'phone' in self.cleaned_data:
                self.user.phone = self.cleaned_data['phone']
            if 'blood_group' in self.cleaned_data:
                self.user.blood_group = self.cleaned_data['blood_group']
            if 'date_of_birth' in self.cleaned_data:
                self.user.date_of_birth = self.cleaned_data['date_of_birth']
            if 'address' in self.cleaned_data:
                self.user.address = self.cleaned_data['address']
            self.user.save()

            # Create or update DonorProfile
            donor_profile = super().save(commit=False)
            donor_profile.user = self.user
            donor_profile.age=self.cleaned_data.get('age')
            donor_profile.gender=self.cleaned_data.get('gender')
            donor_profile.organs_to_donate=self.cleaned_data.get('organs_to_donate')
            donor_profile.medical_fitness_status=self.cleaned_data.get('medical_fitness_status')
            donor_profile.medical_fitness_certificate=self.cleaned_data.get('medical_fitness_certificate')
            donor_profile.lab_reports=self.cleaned_data.get('lab_reports')
            donor_profile.id_proof=self.cleaned_data.get('id_proof')
            donor_profile.is_living_donor=self.cleaned_data.get('is_living_donor', True)
            donor_profile.donation_after_death=self.cleaned_data.get('donation_after_death', True)
            donor_profile.height=self.cleaned_data.get('height') if self.cleaned_data.get('height') and self.cleaned_data['height'] != '' else None
            donor_profile.weight=self.cleaned_data.get('weight') if self.cleaned_data.get('weight') and self.cleaned_data['weight'] != '' else None
            donor_profile.medical_conditions=self.cleaned_data.get('medical_conditions', '')
            donor_profile.medications=self.cleaned_data.get('medications', '')
            donor_profile.taking_medications=self.cleaned_data.get('taking_medications', 'no')
            donor_profile.consent=self.cleaned_data.get('consent', False)
            
            print(f"Creating donor profile for logged-in user: {self.user.username}")
            print(f"Profile data: age={donor_profile.age}, gender={donor_profile.gender}")
            
            if commit:
                donor_profile.save()
                print(f"Donor profile saved with ID: {donor_profile.id}")

            return self.user
        else:
            # Fallback to original behavior if no user provided
            user_data = {}
            user_fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'blood_group', 'date_of_birth', 'address']
            
            for field in user_fields:
                if field in self.cleaned_data:
                    user_data[field] = self.cleaned_data[field]
            
            # Create User object
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                user_type='donor',
                phone=user_data.get('phone', ''),
                blood_group=user_data.get('blood_group', ''),
                date_of_birth=user_data.get('date_of_birth'),
                address=user_data.get('address', '')
            )
            
            # Create DonorProfile
            donor_profile = super().save(commit=False)
            donor_profile.user = user
            donor_profile.age=self.cleaned_data.get('age')
            donor_profile.gender=self.cleaned_data.get('gender')
            donor_profile.organs_to_donate=self.cleaned_data.get('organs_to_donate')
            donor_profile.medical_fitness_status=self.cleaned_data.get('medical_fitness_status')
            donor_profile.medical_fitness_certificate=self.cleaned_data.get('medical_fitness_certificate')
            donor_profile.lab_reports=self.cleaned_data.get('lab_reports')
            donor_profile.id_proof=self.cleaned_data.get('id_proof')
            donor_profile.is_living_donor=self.cleaned_data.get('is_living_donor', True)
            donor_profile.donation_after_death=self.cleaned_data.get('donation_after_death', True)
            donor_profile.height=self.cleaned_data.get('height') if self.cleaned_data.get('height') and self.cleaned_data['height'] != '' else None
            donor_profile.weight=self.cleaned_data.get('weight') if self.cleaned_data.get('weight') and self.cleaned_data['weight'] != '' else None
            donor_profile.medical_conditions=self.cleaned_data.get('medical_conditions', '')
            donor_profile.medications=self.cleaned_data.get('medications', '')
            donor_profile.taking_medications=self.cleaned_data.get('taking_medications', 'no')
            donor_profile.consent=self.cleaned_data.get('consent', False)
            
            print(f"Creating donor profile for user: {user.username}")
            print(f"Profile data: age={donor_profile.age}, gender={donor_profile.gender}")
            
            if commit:
                donor_profile.save()
                print(f"Donor profile saved with ID: {donor_profile.id}")
            
            return user


class RecipientRegistrationForm(forms.ModelForm):
    """Form for recipient registration"""
    age = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '18', 'max': '100'}),
        help_text="Enter your age (18-100 years)"
    )
    gender = forms.ChoiceField(
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    organ_required = forms.ChoiceField(
        choices=User.ORGANS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    urgency_level = forms.ChoiceField(
        choices=User.URGENCY_LEVELS,
        initial='medium',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    blood_type_required = forms.ChoiceField(
        choices=User.BLOOD_GROUPS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    height = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text="Enter height in cm (e.g., 175.5)"
    )
    weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        help_text="Enter weight in kg (e.g., 70.5)"
    )
    doctor_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    hospital_address = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    medical_report = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload your medical report (PDF, JPG, PNG)"
    )
    fitness_certificate = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload your fitness certificate (PDF, JPG, PNG)"
    )
    id_proof = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload your ID proof (Aadhar Card, Passport, Driver's License) - PDF, JPG, PNG"
    )
    transplant_history = forms.ChoiceField(
        choices=[
            ('no', 'No'),
            ('yes', 'Yes'),
        ],
        initial='no',
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-control'}),
        label="Have you had any previous organ transplants?"
    )
    transplant_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Please provide details of your previous transplant history"
    )
    consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I hereby declare that I am voluntarily registering as an organ recipient and have provided all true information to the best of my knowledge."
    )

    class Meta:
        model = RecipientProfile
        fields = ['age', 'gender', 'organ_required', 'urgency_level', 'blood_type_required', 'height', 'weight', 'doctor_name', 
                  'hospital_address', 'medical_report', 'fitness_certificate', 'id_proof', 'transplant_history', 'consent']
        widgets = {
            'organ_required': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_transplant_details(self):
        transplant_details = self.cleaned_data.get('transplant_details', '')
        transplant_history = self.cleaned_data.get('transplant_history')
        
        if transplant_history == 'yes' and not transplant_details.strip():
            raise forms.ValidationError("Please provide details of your previous transplant history.")
        
        return transplant_details

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and age < 18:
            raise forms.ValidationError("You must be at least 18 years old to register as a recipient.")
        return age

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        if user:
            # Add user fields as read-only
            self.fields['username'] = forms.CharField(
                initial=user.username,
                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
                label='Username',
                required=True
            )
            self.fields['email'] = forms.EmailField(
                initial=user.email,
                widget=forms.EmailInput(attrs={'class': 'form-control'}),
                label='Email',
                required=True
            )
            self.fields['first_name'] = forms.CharField(
                initial=user.first_name,
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='First Name',
                required=True
            )
            self.fields['last_name'] = forms.CharField(
                initial=user.last_name,
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='Last Name',
                required=True
            )
            self.fields['phone'] = forms.CharField(
                initial=user.phone,
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                label='Phone',
                required=True
            )
            self.fields['blood_group'] = forms.ChoiceField(
                choices=User.BLOOD_GROUPS,
                initial=user.blood_group,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Blood Group',
                required=True
            )
            self.fields['date_of_birth'] = forms.DateField(
                initial=user.date_of_birth,
                widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                label='Date of Birth',
                required=True
            )
            self.fields['address'] = forms.CharField(
                initial=user.address,
                widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                label='Address',
                required=True
            )

    def save(self, commit=True):
        # Update existing user instead of creating new one
        if self.user:
            # Update user fields from form data
            self.user.user_type = 'recipient'
            if 'email' in self.cleaned_data:
                self.user.email = self.cleaned_data['email']
            if 'first_name' in self.cleaned_data:
                self.user.first_name = self.cleaned_data['first_name']
            if 'last_name' in self.cleaned_data:
                self.user.last_name = self.cleaned_data['last_name']
            if 'phone' in self.cleaned_data:
                self.user.phone = self.cleaned_data['phone']
            if 'blood_group' in self.cleaned_data:
                self.user.blood_group = self.cleaned_data['blood_group']
            if 'date_of_birth' in self.cleaned_data:
                self.user.date_of_birth = self.cleaned_data['date_of_birth']
            if 'address' in self.cleaned_data:
                self.user.address = self.cleaned_data['address']
            self.user.save()

            # Create or update RecipientProfile
            recipient_profile = super().save(commit=False)
            recipient_profile.user = self.user
            recipient_profile.age=self.cleaned_data.get('age')
            recipient_profile.gender=self.cleaned_data.get('gender')
            recipient_profile.organ_required=self.cleaned_data.get('organ_required')
            recipient_profile.urgency_level=self.cleaned_data.get('urgency_level')
            recipient_profile.blood_type_required=self.cleaned_data.get('blood_type_required')
            recipient_profile.height=self.cleaned_data.get('height')
            recipient_profile.weight=self.cleaned_data.get('weight')
            recipient_profile.doctor_name=self.cleaned_data.get('doctor_name')
            recipient_profile.hospital_address=self.cleaned_data.get('hospital_address')
            recipient_profile.medical_report=self.cleaned_data.get('medical_report')
            recipient_profile.fitness_certificate=self.cleaned_data.get('fitness_certificate')
            recipient_profile.id_proof=self.cleaned_data.get('id_proof')
            transplant_history = self.cleaned_data.get('transplant_history')
            transplant_details = self.cleaned_data.get('transplant_details')
            if transplant_history == 'yes':
                recipient_profile.transplant_history = f"Yes: {transplant_details}"
            else:
                recipient_profile.transplant_history = "No"
            recipient_profile.consent=self.cleaned_data.get('consent', False)
            
            if commit:
                recipient_profile.save()

            return self.user
        else:
            # Fallback to original behavior if no user provided
            user_data = {}
            user_fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'blood_group', 'date_of_birth', 'address']

            for field in user_fields:
                if field in self.cleaned_data:
                    user_data[field] = self.cleaned_data[field]

            # Create User object
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                user_type='recipient',
                phone=user_data.get('phone', ''),
                blood_group=user_data.get('blood_group', ''),
                date_of_birth=user_data.get('date_of_birth'),
                address=user_data.get('address', '')
            )

            # Create RecipientProfile
            recipient_profile = super().save(commit=False)
            recipient_profile.user = user
            recipient_profile.age=self.cleaned_data.get('age')
            recipient_profile.gender=self.cleaned_data.get('gender')
            recipient_profile.organ_required=self.cleaned_data.get('organ_required')
            recipient_profile.urgency_level=self.cleaned_data.get('urgency_level')
            recipient_profile.blood_type_required=self.cleaned_data.get('blood_type_required')
            recipient_profile.height=self.cleaned_data.get('height')
            recipient_profile.weight=self.cleaned_data.get('weight')
            recipient_profile.doctor_name=self.cleaned_data.get('doctor_name')
            recipient_profile.hospital_address=self.cleaned_data.get('hospital_address')
            recipient_profile.medical_report=self.cleaned_data.get('medical_report')
            recipient_profile.fitness_certificate=self.cleaned_data.get('fitness_certificate')
            recipient_profile.id_proof=self.cleaned_data.get('id_proof')
            transplant_history = self.cleaned_data.get('transplant_history')
            transplant_details = self.cleaned_data.get('transplant_details')
            if transplant_history == 'yes':
                recipient_profile.transplant_history = f"Yes: {transplant_details}"
            else:
                recipient_profile.transplant_history = "No"
            recipient_profile.consent=self.cleaned_data.get('consent', False)
            
            if commit:
                recipient_profile.save()
            
            return user


class LoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration ID or Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    remember = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
