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



from .models import User



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



    # Check if user is logged in



    if request.user.is_authenticated:



        # Check if user already has a registration



        has_donor_profile = hasattr(request.user, 'donor_profile')



        has_recipient_profile = hasattr(request.user, 'recipient_profile')



        



        # If user already has a registration, show appropriate message



        if has_donor_profile and has_recipient_profile:



            # Remove "already registered" error message - user can register multiple types



            return redirect('main:dashboard')



        elif has_donor_profile:



            return redirect('main:dashboard')



        elif has_recipient_profile:



            return redirect('main:dashboard')



        



        # User is logged in but not registered yet, create forms with user data



        donor_form = DonorRegistrationForm(user=request.user)



        recipient_form = RecipientRegistrationForm(user=request.user)



    else:



        # User is not logged in, create empty forms



        donor_form = DonorRegistrationForm()



        recipient_form = RecipientRegistrationForm()



    



    if request.method == 'POST':



        # Handle AJAX requests



        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':



            return handle_ajax_registration(request)



        



        # Handle regular form submission



        elif 'donor_submit' in request.POST:



            # Check if user already exists (for logged-in users)



            if request.user.is_authenticated:



                has_donor_profile = hasattr(request.user, 'donor_profile')



                has_recipient_profile = hasattr(request.user, 'recipient_profile')



                



                # Process donor registration for logged-in user



                donor_form = DonorRegistrationForm(request.POST, request.FILES, user=request.user)



                



            else:



                # Process donor registration for new user



                donor_form = DonorRegistrationForm(request.POST, request.FILES)



            



            if donor_form.is_valid():



                user = donor_form.save()



                



                # Set user as pending approval



                user.verification_status = 'pending'



                user.save()



                



                # Log activity



                ActivityLog.objects.create(



                    user=user,



                    activity_type='registration',



                    description=f'Donor registration submitted - pending admin approval'



                )



                



                # Don't log in user - they need admin approval first



                # Remove success message - only show error messages
                messages.error(request, 'Please correct the errors below.')



                return redirect('main:register')



            else:



                # Simple error handling - let Django handle field errors



                messages.error(request, 'Please correct the errors below.')



                return render(request, 'register.html', {



                    'donor_form': donor_form,



                    'recipient_form': RecipientRegistrationForm(),



                    'user_logged_in': request.user.is_authenticated



                })



        



        elif 'recipient_submit' in request.POST:



            print("Processing regular recipient form submission...")



            



            # Check if user already exists (for logged-in users)



            if request.user.is_authenticated:



                has_donor_profile = hasattr(request.user, 'donor_profile')



                has_recipient_profile = hasattr(request.user, 'recipient_profile')



                



                # Process recipient registration for logged-in user



                recipient_form = RecipientRegistrationForm(request.POST, request.FILES, user=request.user)



                



            else:



                # Process recipient registration for new user



                recipient_form = RecipientRegistrationForm(request.POST, request.FILES)



            



            if recipient_form.is_valid():



                user = recipient_form.save()



                



                # Set user as pending approval



                user.verification_status = 'pending'



                user.save()



                



                # Log activity



                ActivityLog.objects.create(



                    user=user,



                    activity_type='registration',



                    description=f'Recipient registration submitted - pending admin approval'



                )



                



                # Don't log in user - they need admin approval first



                # Remove success message - only show error messages
                messages.error(request, 'Please correct the errors below.')



                return redirect('main:register')



            else:



                # If form is invalid and user is not logged in, create empty form



                if not request.user.is_authenticated:



                    donor_form = DonorRegistrationForm()



                messages.error(request, 'Please correct the errors below.')



    



    context = {



        'donor_form': donor_form,



        'recipient_form': recipient_form,



        'user_logged_in': request.user.is_authenticated



    }



    return render(request, 'register.html', context)











def handle_ajax_registration(request):



    """Handle AJAX registration from original form"""



    try:



        print(f"=== AJAX REGISTRATION DEBUG ===")



        print(f"POST data keys: {list(request.POST.keys())}")



        print(f"FILES data keys: {list(request.FILES.keys())}")



        



        if 'donor_submit' in request.POST:



            print("Processing donor registration...")



            



            # Check if user already exists (for logged-in users)



            if request.user.is_authenticated:



                has_donor_profile = hasattr(request.user, 'donor_profile')



                has_recipient_profile = hasattr(request.user, 'recipient_profile')



                



                # Process donor registration for logged-in user



                donor_form = DonorRegistrationForm(request.POST, request.FILES, user=request.user)



                print(f"Logged-in user form created: {donor_form}")



                



            else:



                # Process donor registration for new user



                donor_form = DonorRegistrationForm(request.POST, request.FILES)



                print(f"New user form created: {donor_form}")



            



            print(f"Form is valid: {donor_form.is_valid()}")



            if not donor_form.is_valid():



                print(f"Form errors: {donor_form.errors}")



                return JsonResponse({



                    'success': False,



                    'errors': donor_form.errors



                })



            



            # Save the form



            print("Saving donor form...")



            user = donor_form.save()



            print(f"User saved: {user.username}")



            



            # Log in the user if they weren't already logged in



            if not request.user.is_authenticated:



                from django.contrib.auth import login



                login(request, user)



                print("User logged in")



            



            # Log activity



            ActivityLog.objects.create(



                user=user,



                activity_type='registration',



                description=f'Donor registration completed'



            )



            



            print("Donor registration completed successfully")



            return JsonResponse({



                'success': True,



                'message': 'Donor registration completed successfully!'



            })



            



        elif 'recipient_submit' in request.POST:



            print("Processing recipient registration...")



            



            # Check if user already exists (for logged-in users)



            if request.user.is_authenticated:



                has_donor_profile = hasattr(request.user, 'donor_profile')



                has_recipient_profile = hasattr(request.user, 'recipient_profile')



                



                # Process recipient registration for logged-in user



                recipient_form = RecipientRegistrationForm(request.POST, request.FILES, user=request.user)



                print(f"Logged-in user recipient form created: {recipient_form}")



                



            else:



                # Process recipient registration for new user



                recipient_form = RecipientRegistrationForm(request.POST, request.FILES)



                print(f"New user recipient form created: {recipient_form}")



            



            print(f"Recipient form is valid: {recipient_form.is_valid()}")



            if not recipient_form.is_valid():



                print(f"Recipient form errors: {recipient_form.errors}")



                return JsonResponse({



                    'success': False,



                    'errors': recipient_form.errors



                })



            



            # Save the form



            print("Saving recipient form...")



            user = recipient_form.save()



            print(f"Recipient user saved: {user.username}")



            



            # Log in the user if they weren't already logged in



            if not request.user.is_authenticated:



                from django.contrib.auth import login



                login(request, user)



                print("Recipient user logged in")



            



            # Log activity



            ActivityLog.objects.create(



                user=user,



                activity_type='registration',



                description=f'Recipient registration completed'



            )



            



            print("Recipient registration completed successfully")



            return JsonResponse({



                'success': True,



                'message': 'Recipient registration completed successfully!'



            })



        else:



            return JsonResponse({



                'success': False,



                'error': 'Invalid form submission'



            })



            



    except Exception as e:



        import traceback



        error_details = traceback.format_exc()



        print(f"=== REGISTRATION ERROR DEBUG ===")



        print(f"Error type: {type(e).__name__}")



        print(f"Error message: {str(e)}")



        print(f"Full traceback:")



        print(error_details)



        print(f"=== END ERROR DEBUG ===")



        



        # Try to get more specific error information



        error_msg = str(e)



        



        # Check for common database errors



        if "UNIQUE constraint" in error_msg:



            error_msg = "This username or email is already registered. Please use different credentials."



        elif "NOT NULL constraint" in error_msg:



            error_msg = "Please fill in all required fields."



        elif "foreign key constraint" in error_msg:



            error_msg = "There was an error with your registration data. Please try again."



        elif "IntegrityError" in error_msg:



            error_msg = "Data integrity error. Please check your information and try again."



        



        return JsonResponse({



            'success': False,



            'error': error_msg,



            'error_type': type(e).__name__,



            'traceback': error_details



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



            



            # Check if this is an AJAX request



            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'



            



            if not identifier or not password:



                error_msg = 'Please enter both email and password.'



                if is_ajax:



                    return JsonResponse({'success': False, 'message': error_msg})



                else:



                    messages.error(request, error_msg)



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



                error_msg = f'No account found with this {search_field}: {identifier}'



                if is_ajax:



                    return JsonResponse({'success': False, 'message': error_msg})



                else:



                    messages.error(request, error_msg)



                    return render(request, 'login.html', {'form': LoginForm()})



            if not user.check_password(password):



                error_msg = 'The password you entered is incorrect. Please try again.'



                if is_ajax:



                    return JsonResponse({'success': False, 'message': error_msg})



                else:



                    messages.error(request, error_msg)



                    return render(request, 'login.html', {'form': LoginForm()})



            # All validations passed - proceed with login (allow all users to log in)



            login(request, user)



            ActivityLog.objects.create(



                user=user,



                activity_type='login',



                description=f'User logged in with: {identifier} ({search_field})'



            )



            # Determine redirect URL



            if user.user_type == 'admin':



                redirect_url = reverse('main:admin_dashboard')



            else:



                # All non-admin users go to dashboard (regardless of user_type)



                redirect_url = reverse('main:dashboard')



            if is_ajax:



                return JsonResponse({



                    'success': True, 



                    'message': 'Login successful!',



                    'redirect': redirect_url



                })



            else:



                return redirect(redirect_url)



    # Handle GET request - show login form



    return render(request, 'login.html', {'form': LoginForm()})











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



            # Create sign up data record (now stored directly in User model)



            user.signup_ip = request.META.get('REMOTE_ADDR')



            user.signup_device = request.META.get('HTTP_USER_AGENT', '')



            user.signup_browser = request.META.get('HTTP_USER_AGENT', '')



            user.signup_referrer = request.META.get('HTTP_REFERER', '')



            user.signup_utm_source = request.POST.get('utm_source', '')



            user.signup_utm_medium = request.POST.get('utm_medium', '')



            user.signup_utm_campaign = request.POST.get('utm_campaign', '')



            user.is_first_signup = True



            user.signup_completed = True



            user.save()



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



            registration_id = profile.registration_id



        except DonorProfile.DoesNotExist:



            profile = DonorProfile.objects.create(user=user)



            registration_id = profile.registration_id



    elif user.user_type == 'recipient':



        try:



            profile = user.recipient_profile



            registration_id = profile.registration_id



        except RecipientProfile.DoesNotExist:



            profile = RecipientProfile.objects.create(user=user)



            registration_id = profile.registration_id



    else:



        profile = None



        registration_id = None



    # Get user messages



    user_messages = Message.objects.filter(user=user, is_read=False).order_by('-sent_at')



    # Get verification status



    verification_requests = VerificationRequest.objects.filter(user=user).order_by('-created_at')



    context = {



        'user': user,



        'profile': profile,



        'registration_id': registration_id,



        'messages': user_messages,



        'verification_requests': verification_requests,



        'verification_status': user.verification_status,



        'is_verified': user.is_verified,



        'created_at': user.created_at,



    }



    return render(request, 'user-dashboard.html', context)











def admin_login(request):



    """Admin login view"""



    if request.method == 'POST':



        username = request.POST.get('username')



        password = request.POST.get('password')



        # Check if this is an AJAX request



        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'



        # Authenticate using Django's authenticate function



        user = authenticate(request, username=username, password=password)



        if user is not None and user.user_type == 'admin':



            login(request, user)



            if is_ajax:



                return JsonResponse({



                    'success': True, 



                    'redirect': reverse('main:admin_dashboard')



                })



            else:



                return redirect('main:admin_dashboard')



        else:



            # Determine specific error message



            if user is None:



                # User doesn't exist or password is wrong - check if username exists



                try:



                    # Check if username exists



                    User.objects.get(username=username)



                    error_msg = 'The password you entered is incorrect.'



                except User.DoesNotExist:



                    error_msg = 'The username you entered does not exist.'



            else:



                # User exists but is not admin



                error_msg = 'The password you entered is incorrect.'



            if is_ajax:



                return JsonResponse({'success': False, 'message': error_msg})



            else:



                messages.error(request, error_msg)



    



    return render(request, 'main/admin_login.html')











@login_required



def refresh_pending_verifications(request):



    """AJAX endpoint to refresh pending verifications list"""



    if request.user.user_type != 'admin':



        return JsonResponse({'error': 'Unauthorized'}, status=403)



    



    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':



        # Get pending users



        pending_users = User.objects.filter(verification_status='pending').order_by('-updated_at')



        



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



    



    def is_blood_compatible(recipient_blood, donor_blood):



        """Check if donor blood is compatible with recipient blood type"""



        # Blood type compatibility chart



        compatibility = {



            'O+': ['O+', 'O-'],



            'O-': ['O-', 'O+', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'],



            'A+': ['A+', 'A-', 'O+', 'O-'],



            'A-': ['A-', 'A+', 'O-', 'O+'],



            'B+': ['B+', 'B-', 'O+', 'O-'],



            'B-': ['B-', 'B+', 'O-', 'O+'],



            'AB+': ['AB+', 'AB-', 'A+', 'A-', 'B+', 'B-', 'O+', 'O-'],



            'AB-': ['AB-', 'AB+', 'A-', 'A+', 'B-', 'B+', 'O-', 'O+']



        }



        return donor_blood in compatibility.get(recipient_blood, [])



    



    # Add cache control headers to prevent caching



    response = None



    



    # Get filter parameter



    filter_type = request.GET.get('filter', 'all')



    



    # Get statistics (only users with completed registration forms)



    users_with_profiles = User.objects.filter(

        Q(donor_profile__isnull=False) | Q(recipient_profile__isnull=False)

    ).exclude(user_type='admin').order_by('-updated_at')



    



    total_users = users_with_profiles.count()



    total_donors = users_with_profiles.filter(user_type='donor').count()



    total_recipients = users_with_profiles.filter(user_type='recipient').count()



    pending_verifications = users_with_profiles.filter(verification_status='pending').count()



    approved_profiles = users_with_profiles.filter(verification_status='approved').count()



    rejected_profiles = users_with_profiles.filter(verification_status='rejected').count()



    



    # Filter users based on filter parameter (only users with completed registration forms)



    base_users = users_with_profiles



    



    if filter_type == 'pending':



        users = base_users.filter(verification_status='pending')



    elif filter_type == 'approved':



        users = base_users.filter(verification_status='approved')



    elif filter_type == 'rejected':



        users = base_users.filter(verification_status='rejected')



    elif filter_type == 'donor':



        users = base_users.filter(user_type='donor')



    elif filter_type == 'recipient':



        users = base_users.filter(user_type='recipient')



    elif filter_type == 'matched':



        # Get matched users - donors with compatible blood type and matching organ as recipients



        matched_users = []



        donors = base_users.filter(user_type='donor', verification_status='approved')



        recipients = base_users.filter(user_type='recipient', verification_status='approved')



        



        print(f"=== DEBUG MATCHED USERS ===")



        print(f"Total donors: {donors.count()}")



        print(f"Total recipients: {recipients.count()}")



        



        for recipient in recipients:



            if hasattr(recipient, 'recipient_profile') and recipient.recipient_profile:



                print(f"Processing recipient: {recipient.username}")



                print(f"  Blood group: {recipient.blood_group}")



                print(f"  Required organ: {recipient.recipient_profile.organ_required}")



                



                # Find donors with compatible blood type



                compatible_donors = []



                for donor in donors:



                    if hasattr(donor, 'donor_profile') and donor.donor_profile:



                        # Check blood type compatibility



                        if is_blood_compatible(recipient.blood_group, donor.blood_group):



                            # Check organ matching



                            donor_organs = donor.donor_profile.organs_to_donate or []



                            recipient_organ = recipient.recipient_profile.organ_required



                            



                            print(f"  Donor {donor.username} blood: {donor.blood_group} (compatible)")



                            print(f"  Donor {donor.username} organs: {donor_organs}")



                            print(f"  Recipient organ: {recipient_organ}")



                            



                            # Check if recipient's required organ is in donor's organs to donate



                            if recipient_organ in donor_organs:



                                compatible_donors.append(donor)



                                print(f"  -> MATCH FOUND: {donor.username}")



                



                print(f"  Compatible donors for {recipient.username}: {len(compatible_donors)}")



                



                # Add both recipient and matching donors to the list



                if compatible_donors:  # Only add if there are matches



                    matched_users.append(recipient)



                    matched_users.extend(compatible_donors)



        



        # Remove duplicates and sort



        users = list(set(matched_users))



        users.sort(key=lambda x: x.updated_at, reverse=True)



        



        print(f"Total matched users: {len(users)}")



        print(f"=== END DEBUG ===")



        



        # If no matches found, show empty list (not all users)



        if len(users) == 0:



            print("No matches found, showing empty list")



            users = []



    else:



        users = base_users



    



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











def test_register(request):



    """Simple test registration view"""



    if request.method == 'POST':



        if 'donor_submit' in request.POST:



            print("=== TEST REGISTRATION DEBUG ===")



            print(f"POST data: {dict(request.POST)}")



            print(f"FILES data: {dict(request.FILES)}")



            



            # Create form with POST data and files



            donor_form = DonorRegistrationForm(request.POST, request.FILES)



            



            print(f"Form is valid: {donor_form.is_valid()}")



            if not donor_form.is_valid():



                print(f"Form errors: {donor_form.errors}")



                return render(request, 'test_register.html', {'form': donor_form})



            



            # Save the form



            try:



                user = donor_form.save()



                print(f"User saved: {user.username}")



                



                # Log in the user



                from django.contrib.auth import login



                login(request, user)



                



                # Remove success message - only show error messages



                return redirect('main:dashboard')



                



            except Exception as e:



                print(f"Save error: {e}")



                import traceback



                traceback.print_exc()



                return render(request, 'test_register.html', {'form': donor_form, 'error': str(e)})



    



    # GET request - show empty form



    form = DonorRegistrationForm()



    return render(request, 'test_register.html', {'form': form})











@login_required



def logout(request):



    """Logout view"""



    ActivityLog.objects.create(



        user=request.user,



        activity_type='logout',



        description='User logged out'



    )



    auth_logout(request)



    



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



        



        # Send approval email (wrapped in try-catch to avoid blocking approval)
        try:
            send_verification_email(user, 'approved')
        except Exception as e:
            # Email failed but don't block the approval process
            pass
        
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



