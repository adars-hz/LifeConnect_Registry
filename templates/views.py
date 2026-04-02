from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import User, SignUpData
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import User, DonorProfile, RecipientProfile, Document, VerificationRequest, Message, ActivityLog
from .forms import DonorRegistrationForm, RecipientRegistrationForm, LoginForm
import json
import logging

logger = logging.getLogger(__name__)


def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'main/errors/404.html', status=404)


def custom_500(request):
    """Custom 500 error handler"""
    return render(request, 'main/errors/500.html', status=500)


def home(request):
    """Home page with statistics"""
    context = {
        'total_donors': User.objects.filter(user_type='donor').count(),
        'total_recipients': User.objects.filter(user_type='recipient').count(),
        'approved_profiles': User.objects.filter(is_verified=True).count(),
        'pending_verifications': User.objects.filter(verification_status='pending').count(),
    }
    response = render(request, 'index.html', context)
    # Add cache control headers to prevent caching of authenticated pages
    if request.user.is_authenticated:
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
    return response


def about(request):
    """About organ donation page"""
    return render(request, 'about.html')


def register(request):
    """Registration page with donor/recipient forms"""
    donor_form = DonorRegistrationForm()
    recipient_form = RecipientRegistrationForm()
    
    if request.method == 'POST':
        # Handle AJAX requests from original form
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_registration(request)
        
        # Handle Django form submissions
        if 'donor_submit' in request.POST:
            donor_form = DonorRegistrationForm(request.POST, request.FILES)
            if donor_form.is_valid():
                user = donor_form.save()
                messages.success(request, 'Registration successful!')
                ActivityLog.objects.create(
                    user=user,
                    activity_type='registration',
                    description=f'Donor registration completed'
                )
                return redirect('login')
        
        elif 'recipient_submit' in request.POST:
            recipient_form = RecipientRegistrationForm(request.POST, request.FILES)
            if recipient_form.is_valid():
                user = recipient_form.save()
                messages.success(request, 'Registration successful!')
                ActivityLog.objects.create(
                    user=user,
                    activity_type='registration',
                    description=f'Recipient registration completed'
                )
                return redirect('login')
    
    context = {
        'donor_form': donor_form,
        'recipient_form': recipient_form
    }
    return render(request, 'register.html', context)


def handle_ajax_registration(request):
    """Handle AJAX registration from original form"""
    try:
        if 'donor_submit' in request.POST:
            # Process donor registration
            user_data = extract_user_data(request, 'donor')
            profile_data = extract_donor_profile_data(request)
            
            # Create user
            user = User.objects.create_user(**user_data)
            
            # Create donor profile
            DonorProfile.objects.create(user=user, **profile_data)
            
            # Log activity
            ActivityLog.objects.create(
                user=user,
                activity_type='registration',
                description=f'Donor registration completed'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Registration successful!'
            })
            
        elif 'recipient_submit' in request.POST:
            # Process recipient registration
            user_data = extract_user_data(request, 'recipient')
            profile_data = extract_recipient_profile_data(request)
            
            # Create user
            user = User.objects.create_user(**user_data)
            
            # Create recipient profile
            RecipientProfile.objects.create(user=user, **profile_data)
            
            # Log activity
            ActivityLog.objects.create(
                user=user,
                activity_type='registration',
                description=f'Recipient registration completed'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Registration successful!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid form submission'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def extract_user_data(request, user_type):
    """Extract user data from form"""
    data = request.POST
    files = request.FILES
    
    # Handle full name split
    full_name = data.get('name', '').strip()
    if ' ' in full_name:
        first_name, last_name = full_name.split(' ', 1)
    else:
        first_name = full_name
        last_name = ''
    
    # Generate unique username
    base_username = data.get('username', '').strip()
    if not base_username:
        # Generate username from name if not provided
        base_username = full_name.lower().replace(' ', '_').replace('-', '_')
    
    # Ensure username is unique
    username = generate_unique_username(base_username)
    
    # Convert age to date of birth (approximate)
    age = data.get('age', '')
    date_of_birth = None
    if age:
        try:
            from datetime import date, timedelta
            birth_year = date.today().year - int(age)
            date_of_birth = date(birth_year, 1, 1)  # Approximate birth date
        except (ValueError, TypeError):
            pass
    
    return {
        'username': username,
        'email': data.get('email', ''),
        'password': data.get('password', ''),
        'first_name': first_name,
        'last_name': last_name,
        'user_type': user_type,
        'phone': data.get('phone', ''),
        'blood_group': data.get('blood', ''),
        'address': data.get('address', ''),
        'date_of_birth': date_of_birth,
        'id_proof': files.get('idProof'),
        'profile_picture': files.get('photo'),
    }


def generate_unique_username(base_username):
    """Generate a unique username"""
    import random
    import string
    
    # Clean up the username
    username = base_username.lower()
    username = ''.join(c for c in username if c.isalnum() or c == '_')
    
    # If username is empty, generate a random one
    if not username:
        username = f"user{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
    
    # Check if username exists, if so, add counter
    original_username = username
    counter = 1
    
    # Always check for duplicates
    while True:
        try:
            from main.models import User
            User.objects.get(username=username)
            # Username exists, add counter
            username = f"{original_username}_{counter}"
            counter += 1
        except User.DoesNotExist:
            # Username is available
            break
    
    return username


def extract_donor_profile_data(request):
    """Extract donor profile data from form"""
    data = request.POST
    files = request.FILES
    
    # Get selected organs
    organs = data.getlist('organs', [])
    
    return {
        'organs_to_donate': organs,
        'medical_fitness_status': data.get('fitness', 'pending'),
        'medical_fitness_certificate': files.get('certificate'),
        'doctor_approval': files.get('doctor_approval'),
        'is_living_donor': True,
        'donation_after_death': True,
        'height': data.get('height') if data.get('height') and data.get('height').strip() else None,
        'weight': data.get('weight') if data.get('weight') and data.get('weight').strip() else None,
        'medical_conditions': data.get('medical_conditions', ''),
        'medications': data.get('medications', ''),
    }


def extract_recipient_profile_data(request):
    """Extract recipient profile data from form"""
    data = request.POST
    files = request.FILES
    
    return {
        'organ_required': data.get('organ', ''),
        'urgency_level': data.get('urgency', 'medium'),
        'blood_type_required': '',
        'hospital_name': data.get('hospital', ''),
        'doctor_name': data.get('doctor', ''),
        'hospital_address': '',
        'doctor_contact': '',
        'diagnosis_date': None,
        'medical_report': files.get('certificate'),
        'eligibility_certificate': None,
        'transplant_history': '',
        'additional_notes': '',
    }


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        # Handle form submission from login page
        if 'identifier' in request.POST and 'password' in request.POST:
            # Handle login with email (from login form)
            identifier = request.POST.get('identifier').strip()
            password = request.POST.get('password')
            
            if not identifier or not password:
                messages.error(request, 'Please enter both email and password.')
                return render(request, 'login.html', {'form': LoginForm()})
            
            # Try to find user by email or username
            user = None
            search_field = None
            
            try:
                # Try by email first
                user = User.objects.get(email__iexact=identifier)
                search_field = 'Email'
            except User.DoesNotExist:
                try:
                    # Then try by username
                    user = User.objects.get(username__iexact=identifier)
                    search_field = 'Username'
                except User.DoesNotExist:
                    user = None
                    search_field = 'Username/Email'
            
            # Explicit validation checks
            if user is None:
                messages.error(request, f'No account found with this {search_field}: {identifier}')
                return render(request, 'login.html', {'form': LoginForm()})
            
            if not user.check_password(password):
                messages.error(request, 'Incorrect password. Please try again.')
                return render(request, 'login.html', {'form': LoginForm()})
            
            # Additional validation - check if user is verified
            if user.verification_status != 'approved':
                messages.error(request, f'Your account is {user.verification_status}. Please contact admin for approval.')
                return render(request, 'login.html', {'form': LoginForm()})
            
            # All validations passed - proceed with login
            login(request, user)
            ActivityLog.objects.create(
                user=user,
                activity_type='login',
                description=f'User logged in with: {identifier} ({search_field})'
            )
            
            messages.success(request, f'Login successful! Welcome, {user.get_full_name() or user.username}.')
            
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect('main:admin_dashboard')
            else:
                return redirect('main:dashboard')
        else:
            # Handle form submission from LoginForm
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                
                if not username or not password:
                    messages.error(request, 'Please enter both username and password.')
                    return render(request, 'login.html', {'form': form})
                
                # Try to find user by username or email
                user = None
                try:
                    user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
                except User.DoesNotExist:
                    user = None
                
                # Explicit validation checks
                if user is None:
                    messages.error(request, f'No account found with username: {username}')
                    return render(request, 'login.html', {'form': form})
                
                if not user.check_password(password):
                    messages.error(request, 'Incorrect password. Please try again.')
                    return render(request, 'login.html', {'form': form})
                
                # Additional validation - check if user is verified
                if user.verification_status != 'approved':
                    messages.error(request, f'Your account is {user.verification_status}. Please contact admin for approval.')
                    return render(request, 'login.html', {'form': form})
                
                # All validations passed - proceed with login
                login(request, user)
                ActivityLog.objects.create(
                    user=user,
                    activity_type='login',
                    description=f'User logged in with: {username}'
                )
                
                messages.success(request, f'Login successful! Welcome, {user.get_full_name() or user.username}.')
                
                # Redirect based on user type
                if user.user_type == 'admin':
                    return redirect('main:admin_dashboard')
                else:
                    return redirect('main:dashboard')
            else:
                messages.error(request, 'Please correct the errors below.')
                return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@require_http_methods(["GET", "POST"])
@csrf_exempt
def signup(request):
    """Handle user signup via AJAX"""
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            
            # Validation
            if not username or not email or not password:
                return JsonResponse({'success': False, 'error': 'All fields are required'})
            
            if len(password) < 6:
                return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters (letters or numbers)'})
            
            # Check if username already exists
            if User.objects.filter(username__iexact=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists'})
            
            # Check if email already exists
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'success': False, 'error': 'Email already exists'})
            
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type='user',  # Default to user type for modal sign-ups
                verification_status='approved'  # Auto-approve for immediate login
            )
            
            # Create sign up data record
            from main.models import SignUpData
            SignUpData.objects.create(
                user=user,
                signup_ip=request.META.get('REMOTE_ADDR'),
                signup_device=request.META.get('HTTP_USER_AGENT', ''),
                signup_browser=request.META.get('HTTP_USER_AGENT', ''),
                signup_referrer=request.META.get('HTTP_REFERER', ''),
                signup_utm_source=request.POST.get('utm_source', ''),
                signup_utm_medium=request.POST.get('utm_medium', ''),
                signup_utm_campaign=request.POST.get('utm_campaign', ''),
                is_first_signup=True,
                signup_completed=True
            )
            
            # Log the signup activity
            ActivityLog.objects.create(
                user=user,
                activity_type='registration',
                description=f'User {username} signed up with email {email}'
            )
            
            return JsonResponse({
                'success': True, 
                'message': 'Account created successfully! Please login.'
            })
            
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return JsonResponse({'success': False, 'error': 'An error occurred during signup'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def dashboard(request):
    """User dashboard view"""
    user = request.user
    
    # Get user profile based on user type
    if user.user_type == 'donor':
        try:
            profile = user.donor_profile
        except DonorProfile.DoesNotExist:
            profile = DonorProfile.objects.create(user=user)
    elif user.user_type == 'recipient':
        try:
            profile = user.recipient_profile
        except RecipientProfile.DoesNotExist:
            profile = RecipientProfile.objects.create(user=user)
    else:
        profile = None
    
    # Get user messages
    user_messages = Message.objects.filter(user=user, is_read=False).order_by('-sent_at')
    
    # Get verification status
    verification_requests = VerificationRequest.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'profile': profile,
        'messages': user_messages,
        'verification_requests': verification_requests,
    }
    return render(request, 'user-dashboard.html', context)


def admin_login(request):
    """Admin login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate using Django's authenticate function
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.user_type == 'admin':
            login(request, user)
            messages.success(request, 'Admin login successful!')
            return redirect('main:admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')
    
    return render(request, 'main/admin_login.html')


@login_required
def refresh_pending_verifications(request):
    """AJAX endpoint to refresh pending verifications list"""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get pending users
        pending_users = User.objects.filter(verification_status='pending').order_by('-created_at')
        
        # Render the verification list template fragment
        html = render_to_string('admin/partials/verification_list.html', {
            'pending_users': pending_users
        })
        
        return JsonResponse({'html': html})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if request.user.user_type != 'admin':
        return redirect('main:dashboard')
    
    # Add cache control headers to prevent caching
    response = None
    
    # Get filter parameter
    filter_type = request.GET.get('filter', 'all')
    
    # Get statistics (exclude admin users)
    total_users = User.objects.exclude(user_type='admin').count()
    total_donors = User.objects.filter(user_type='donor').count()
    total_recipients = User.objects.filter(user_type='recipient').count()
    pending_verifications = User.objects.filter(verification_status='pending').exclude(user_type='admin').count()
    approved_profiles = User.objects.filter(verification_status='approved').exclude(user_type='admin').count()
    rejected_profiles = User.objects.filter(verification_status='rejected').exclude(user_type='admin').count()
    
    # Filter users based on filter parameter (exclude admin users)
    if filter_type == 'pending':
        users = User.objects.filter(verification_status='pending').exclude(user_type='admin').order_by('-created_at')
    elif filter_type == 'approved':
        users = User.objects.filter(verification_status='approved').exclude(user_type='admin').order_by('-created_at')
    elif filter_type == 'rejected':
        users = User.objects.filter(verification_status='rejected').exclude(user_type='admin').order_by('-created_at')
    else:
        users = User.objects.exclude(user_type='admin').order_by('-created_at')
    
    # Get recent activities - include registrations and verifications (exclude admin users)
    recent_activities = ActivityLog.objects.filter(
        activity_type__in=['verification', 'registration'],
        user__user_type__in=['donor', 'recipient']
    ).order_by('-timestamp')[:10]
    
    context = {
        'total_users': total_users,
        'total_donors': total_donors,
        'total_recipients': total_recipients,
        'pending_verifications': pending_verifications,
        'approved_profiles': approved_profiles,
        'rejected_profiles': rejected_profiles,
        'users': users,
        'current_filter': filter_type,
        'recent_activities': recent_activities,
    }
    response = render(request, 'admin-dashboard.html', context)
    # Add cache control headers to prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
def user_details(request, user_id):
    """View detailed user information including certificates"""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        # Get user profile based on user type
        if user.user_type == 'donor':
            try:
                profile = user.donor_profile
            except DonorProfile.DoesNotExist:
                profile = None
        elif user.user_type == 'recipient':
            try:
                profile = user.recipient_profile
            except RecipientProfile.DoesNotExist:
                profile = None
        else:
            profile = None
        
        # Get user documents
        documents = Document.objects.filter(user=user)
        
        # Get verification requests
        verification_requests = VerificationRequest.objects.filter(user=user).order_by('-created_at')
        
        context = {
            'user': user,
            'profile': profile,
            'documents': documents,
            'verification_requests': verification_requests,
        }
        return render(request, 'admin/user-details.html', context)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)



def faq(request):
    """FAQ page view"""
    return render(request, 'faq.html')


@login_required
def logout(request):
    """Logout view"""
    ActivityLog.objects.create(
        user=request.user,
        activity_type='logout',
        description='User logged out'
    )
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    
    # Create response with cache control headers
    response = redirect('main:home')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
@require_POST
def approve_user(request, user_id):
    """Approve user verification"""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    if user.verification_status == 'pending':
        user.verification_status = 'approved'
        user.is_verified = True
        user.save()
        
        # Send approval email
        send_verification_email(user, 'approved')
        
        # Create message for user
        Message.objects.create(
            user=user,
            message_type='approval',
            subject='Registration Approved',
            content='Congratulations! Your registration has been approved. You can now access your dashboard.',
            is_important=True
        )
        
        # Create activity log
        ActivityLog.objects.create(
            user=user,
            activity_type='verification',
            description=f'User {user.get_full_name|default:user.username} approved by {request.user.username}',
            activity_details=f'Registration ID: {user.registration_id} - Status changed from pending to approved'
        )
        
        return JsonResponse({'success': True, 'message': 'User approved successfully'})
    elif user.verification_status == 'approved':
        return JsonResponse({'error': 'User has already been approved', 'status': 'already_approved'}, status=400)
    elif user.verification_status == 'rejected':
        return JsonResponse({'error': 'User has already been rejected and cannot be approved', 'status': 'already_rejected'}, status=400)
    else:
        return JsonResponse({'error': 'User is not in pending status'}, status=400)


@login_required
def export_data(request):
    """Export user data as CSV"""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_data_export.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Registration ID', 'Name', 'Email', 'Phone', 'User Type', 
        'Blood Group', 'Verification Status', 'Registration Date',
        'Address', 'Date of Birth', 'Gender'
    ])
    
    # Write user data
    users = User.objects.all().order_by('-date_joined')
    for user in users:
        writer.writerow([
            user.registration_id,
            user.get_full_name() or user.username,
            user.email,
            user.phone,
            user.get_user_type_display(),
            user.blood_group,
            user.get_verification_status_display(),
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            user.address,
            user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else '',
            user.get_gender_display() if hasattr(user, 'get_gender_display') else ''
        ])
    
    return response


@login_required
@require_POST
def reject_user(request, user_id):
    """Reject user verification"""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    reason = request.POST.get('reason', '')
    
    if user.verification_status == 'pending':
        user.verification_status = 'rejected'
        user.save()
        
        # Send rejection email
        send_verification_email(user, 'rejected', reason)
        
        # Create message for user
        Message.objects.create(
            user=user,
            message_type='rejection',
            subject='Registration Update',
            content=f'Your registration has been rejected. Reason: {reason}',
            is_important=True
        )
        
        # Create activity log
        ActivityLog.objects.create(
            user=user,
            activity_type='verification',
            description=f'User {user.get_full_name|default:user.username} rejected by {request.user.username}',
            activity_details=f'Registration ID: {user.registration_id} - Status changed from pending to rejected. Reason: {reason}'
        )
        
        return JsonResponse({'success': True, 'message': 'User rejected successfully'})
    elif user.verification_status == 'rejected':
        return JsonResponse({'error': 'User has already been rejected', 'status': 'already_rejected'}, status=400)
    elif user.verification_status == 'approved':
        return JsonResponse({'error': 'User has already been approved and cannot be rejected', 'status': 'already_approved'}, status=400)
    else:
        return JsonResponse({'error': 'User is not in pending status'}, status=400)


@login_required
def send_email_to_user(request, user_id):
    """Send email to user"""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    subject = request.POST.get('subject', 'Life Connect Registry - Verification Update')
    message = request.POST.get('message', '')
    
    try:
        send_mail(
            subject,
            message,
            'info@lifeconnect.org',
            [user.email],
            fail_silently=False,
        )
        
        ActivityLog.objects.create(
            user=user,
            activity_type='email_sent',
            description=f'Email sent to user by {request.user.username}'
        )
        
        return JsonResponse({'success': True, 'message': 'Email sent successfully'})
    except Exception as e:
        return JsonResponse({'error': f'Error sending email: {e}'}, status=500)


def send_verification_email(user, status, reason=''):
    """Send verification status email to user"""
    subject = f"Life Connect Registry - Registration {status.title()}"
    
    if status == 'approved':
        message = f"""
        Dear {user.get_full_name() or user.username},

        Congratulations! Your registration with ID {user.registration_id} has been approved.
        
        You can now log in to your dashboard using:
        - Registration ID: {user.registration_id}
        - Email: {user.email}
        
        Thank you for joining Life Connect Registry.

        Best regards,
        Life Connect Registry Team
        """
    else:
        message = f"""
        Dear {user.get_full_name() or user.username},

        We regret to inform you that your registration with ID {user.registration_id} has been rejected.
        
        Reason: {reason}
        
        If you believe this is an error, please contact our support team.

        Best regards,
        Life Connect Registry Team
        """
    
    try:
        send_mail(
            subject,
            message,
            'info@lifeconnect.org',
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")


@csrf_exempt
@require_POST
def generate_registration_id(request):
    """Generate unique registration ID for AJAX requests"""
    user_type = request.POST.get('user_type', 'donor')
    
    if user_type == 'donor':
        registration_id = f"OD-DON-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    elif user_type == 'recipient':
        registration_id = f"OD-REC-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    else:
        registration_id = f"OD-ADM-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    return JsonResponse({'registration_id': registration_id})
