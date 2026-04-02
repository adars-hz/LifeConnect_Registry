from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    USER_TYPES = [
        ('user', 'Normal User'),  # For modal signups
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
        ('admin', 'Admin'),
    ]
    
    
    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    ORGANS = [
        ('heart', 'Heart'),
        ('kidney', 'Kidney'),
        ('liver', 'Liver'),
        ('lungs', 'Lungs'),
        ('pancreas', 'Pancreas'),
        ('intestine', 'Intestine'),
        ('cornea', 'Cornea'),
        ('skin', 'Skin'),
        ('bone', 'Bone'),
    ]
    
    URGENCY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('fit', 'Fit'),
        ('not_fit', 'Not Fit'),
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic user information
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='donor')
    phone = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    
    # Signup tracking details
    signup_ip = models.GenericIPAddressField(null=True, blank=True)
    signup_device = models.CharField(max_length=255, blank=True)
    signup_browser = models.CharField(max_length=255, blank=True)
    signup_referrer = models.URLField(blank=True)
    signup_utm_source = models.CharField(max_length=255, blank=True)
    signup_utm_medium = models.CharField(max_length=255, blank=True)
    signup_utm_campaign = models.CharField(max_length=255, blank=True)
    is_first_signup = models.BooleanField(default=True)
    signup_completed = models.BooleanField(default=True)
    
    # Profile information
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    
    # Status and timestamps
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        if instance.user_type == 'donor':
            DonorProfile.objects.get_or_create(user=instance)
        elif instance.user_type == 'recipient':
            RecipientProfile.objects.get_or_create(user=instance)


class DonorProfile(models.Model):
    """Extended profile for organ donors"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    
    # Registration information
    registration_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Personal information
    age = models.IntegerField(default=18)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        default='male'
    )
    
    # Medical information
    organs_to_donate = models.JSONField(default=list)  # Store as JSON array
    medical_fitness_status = models.CharField(
        max_length=20,
        choices=[
            ('fit', 'Fit'),
            ('not_fit', 'Not Fit'),
        ],
        default='fit'
    )
    medical_fitness_certificate = models.FileField(upload_to='medical_certificates/', blank=True, null=True)
    doctor_approval = models.FileField(upload_to='doctor_approvals/', blank=True, null=True)
    
    # Donation preferences
    is_living_donor = models.BooleanField(default=True)
    donation_after_death = models.BooleanField(default=True)
    
    # Additional medical details
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    medical_conditions = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    taking_medications = models.CharField(
        max_length=10,
        choices=[
            ('no', 'No'),
            ('yes', 'Yes'),
        ],
        default='no'
    )
    lab_reports = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    consent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'donor_profiles'
        verbose_name = 'Donor Profile'
        verbose_name_plural = 'Donor Profiles'
    
    def __str__(self):
        return f"Donor Profile - {self.user.username}"
    
    def generate_registration_id(self):
        """Generate unique registration ID for donor"""
        import random
        import string
        from datetime import datetime
        
        # Format: LCR-DON-YYYYMMDD-XXXX (LCR = Life Connect Registry, DON = Donor)
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        registration_id = f"LCR-DON-{date_str}-{random_str}"
        
        # Ensure uniqueness
        while DonorProfile.objects.filter(registration_id=registration_id).exists():
            random_str = ''.join(random.choices(string.digits, k=4))
            registration_id = f"LCR-DON-{date_str}-{random_str}"
        
        return registration_id
    
    def save(self, *args, **kwargs):
        # Generate registration ID if it doesn't exist
        if not self.registration_id:
            self.registration_id = self.generate_registration_id()
        super().save(*args, **kwargs)


class RecipientProfile(models.Model):
    """Extended profile for organ recipients"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recipient_profile')
    
    # Registration information
    registration_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Personal information
    age = models.IntegerField(default=18)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        default='male'
    )
    
    # Medical information
    organ_required = models.CharField(max_length=50, choices=User.ORGANS)
    urgency_level = models.CharField(max_length=10, choices=User.URGENCY_LEVELS, default='medium')
    blood_type_required = models.CharField(max_length=5, choices=User.BLOOD_GROUPS, blank=True)
    
    # Medical details
    diagnosis_date = models.DateField(null=True, blank=True)
    medical_report = models.FileField(upload_to='medical_reports/', blank=True, null=True)
    lab_reports = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    fitness_certificate = models.FileField(upload_to='fitness_certificates/', blank=True, null=True)
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)

    # Physical information
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in centimeters")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kilograms")

    # Medical contact information
    doctor_name = models.CharField(max_length=100, null=True, blank=True, help_text="Doctor's full name")
    hospital_name = models.CharField(max_length=200, null=True, blank=True, help_text="Hospital name")
    hospital_address = models.TextField(null=True, blank=True, help_text="Hospital address")

    # Additional information
    transplant_history = models.TextField(blank=True)
    additional_notes = models.TextField(blank=True)
    consent = models.BooleanField(default=False)

    class Meta:
        db_table = 'recipient_profiles'
        verbose_name = 'Recipient Profile'
        verbose_name_plural = 'Recipient Profiles'
    
    def __str__(self):
        return f"Recipient Profile - {self.user.username}"
    
    def generate_registration_id(self):
        """Generate unique registration ID for recipient"""
        import random
        import string
        from datetime import datetime
        
        # Format: LCR-REC-YYYYMMDD-XXXX (LCR = Life Connect Registry, REC = Recipient)
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        registration_id = f"LCR-REC-{date_str}-{random_str}"
        
        # Ensure uniqueness
        while RecipientProfile.objects.filter(registration_id=registration_id).exists():
            random_str = ''.join(random.choices(string.digits, k=4))
            registration_id = f"LCR-REC-{date_str}-{random_str}"
        
        return registration_id
    
    def save(self, *args, **kwargs):
        # Generate registration ID if it doesn't exist
        if not self.registration_id:
            self.registration_id = self.generate_registration_id()
        super().save(*args, **kwargs)


class Document(models.Model):
    """Model for storing uploaded documents"""
    DOCUMENT_TYPES = [
        ('id_proof', 'ID Proof'),
        ('medical_certificate', 'Medical Certificate'),
        ('doctor_approval', 'Doctor Approval'),
        ('profile_picture', 'Profile Picture'),
        ('medical_report', 'Medical Report'),
        ('eligibility_certificate', 'Eligibility Certificate'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'documents'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user.username}"


class VerificationRequest(models.Model):
    """Model for tracking verification requests"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_requests')
    
    # Request details
    request_type = models.CharField(max_length=20, choices=[
        ('registration', 'Registration'),
        ('document_update', 'Document Update'),
        ('profile_update', 'Profile Update'),
    ])
    status = models.CharField(max_length=20, choices=User.STATUS_CHOICES, default='pending')
    
    # Admin actions
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='reviewed_verifications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'verification_requests'
        verbose_name = 'Verification Request'
        verbose_name_plural = 'Verification Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification Request - {self.user.username}"


class Message(models.Model):
    """Model for system messages and notifications"""
    MESSAGE_TYPES = [
        ('system', 'System'),
        ('admin', 'Admin'),
        ('verification', 'Verification'),
        ('approval', 'Approval'),
        ('rejection', 'Rejection'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Message - {self.user.username} - {self.subject}"


class ActivityLog(models.Model):
    """Model for tracking user activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    # Activity details
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Activity - {self.user.username} - {self.activity_type}"
