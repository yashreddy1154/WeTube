from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout


def login_view(request):
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # 1. Grab what the user typed into the form
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # 2. Check the database to see if this user exists with this password
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # 3. If the user exists, log them in (creates the session)
            login(request, user)
            # 4. Send them to a home page!
            return redirect('home') 
        else:
            # If it fails, reload the page and show an error message
            return render(request, 'login/login_page.html', {'error': 'Invalid email or password.'})

    # If they are just visiting the page (GET request), show the blank form
    return render(request, 'login/login_page.html')

# We need a quick "Home" page to send them to after they log in
def home_view(request):
    return render(request, 'login/home.html')

import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

# Get our Custom User model
User = get_user_model()

# --- NEW OTP VIEWS ---

def login_with_otp_view(request):
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 1. Check if a user with this email actually exists in the database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'login/otp_request.html', {'error': 'No account found with this email.'})
        
        # 2. Generate a random 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # 3. Save the OTP and Email temporarily in the user's browser "session"
        request.session['otp'] = otp
        request.session['otp_email'] = email
        
        # 4. Send the Email!
        send_mail(
            subject='Your WeTube Login Code',
            message=f'Your one-time password is: {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        # 5. Send them to the screen to type in the code
        return redirect('verify_otp')
        
    return render(request, 'login/otp_request.html')

def verify_otp_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        # Grab the real OTP and Email that we hid in the session earlier
        saved_otp = request.session.get('otp')
        email = request.session.get('otp_email')
        
        if entered_otp == saved_otp:
            # 1. Success! Find the user and log them in
            user = User.objects.get(email=email)
            login(request, user)
            
            # 2. Clean up our mess (delete the OTP from the session for security)
            del request.session['otp']
            del request.session['otp_email']
            
            return redirect('home')
        else:
            return render(request, 'login/otp_verify.html', {'error': 'Invalid code. Try again.'})
            
    return render(request, 'login/otp_verify.html')
def register_view(request):
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Grab the new fields!
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')

        if password != confirm_password:
            return render(request, 'login/register.html', {'error': 'Passwords do not match.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'login/register.html', {'error': 'Email is already registered.'})

        import random
        otp = str(random.randint(100000, 999999))
        
        # Save EVERYTHING in the session
        request.session['reg_email'] = email
        request.session['reg_password'] = password
        request.session['reg_first_name'] = first_name
        request.session['reg_last_name'] = last_name
        request.session['reg_dob'] = dob
        request.session['reg_gender'] = gender
        request.session['reg_otp'] = otp
        
        # Send Verification Email (same as before)
        send_mail(
            subject='Verify your WeTube Account',
            message=f'Your account creation code is: {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return redirect('verify_register_otp')

    return render(request, 'login/register.html')


def verify_register_otp_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        saved_otp = request.session.get('reg_otp')
        email = request.session.get('reg_email')
        password = request.session.get('reg_password')
        
        # Grab the new fields from the session
        first_name = request.session.get('reg_first_name')
        last_name = request.session.get('reg_last_name')
        dob = request.session.get('reg_dob')
        gender = request.session.get('reg_gender')
        
        if entered_otp == saved_otp:
            # Create the user WITH the new details!
            user = User.objects.create_user(
                email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                gender=gender
            )
            
            # Send Welcome Email (same as before)
            send_mail(
                subject='Welcome to WeTube!',
                message=f'Hi {first_name}, your WeTube account has been successfully created. Welcome aboard!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            login(request, user)
            
            # Clean up the session
            keys_to_delete = ['reg_email', 'reg_password', 'reg_first_name', 'reg_last_name', 'reg_dob', 'reg_gender', 'reg_otp']
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]
            
            return redirect('home')
        else:
            return render(request, 'login/register_otp_verify.html', {'error': 'Invalid code. Try again.'})
            
    return render(request, 'login/register_otp_verify.html')


from django.contrib.auth.decorators import login_required

# @login_required forces them to be logged in to see this page!
@login_required 
def profile_view(request):
    if request.method == 'POST':
        # Update the currently logged-in user's details
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        
        # Only update DOB if they actually typed one in, otherwise keep old one
        dob_input = request.POST.get('dob')
        if dob_input:
            request.user.dob = dob_input
            
        request.user.gender = request.POST.get('gender')
        request.user.save() # Save it to the database!
        
        return redirect('home') # Send them back home after updating

    return render(request, 'login/profile.html')


def logout_view(request):
    
    
    from django.contrib.auth import logout # Local import just to be safe
    logout(request) 
    return redirect('login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 1. Check if the user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'login/forgot_password.html', {'error': 'No account found with this email.'})
        
        # 2. Generate OTP and save to session
        import random
        otp = str(random.randint(100000, 999999))
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        
        # 3. Send the Reset Email
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject='Reset Your WeTube Password',
            message=f'Your password reset code is: {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        # 4. Redirect to the screen where they type the new password
        return redirect('reset_password')
        
    return render(request, 'login/forgot_password.html')


def reset_password_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        saved_otp = request.session.get('reset_otp')
        email = request.session.get('reset_email')
        
        # 1. Check if the OTP is correct
        if entered_otp != saved_otp:
            return render(request, 'login/reset_password.html', {'error': 'Invalid reset code. Try again.'})
            
        # 2. Check if passwords match
        if new_password != confirm_password:
            return render(request, 'login/reset_password.html', {'error': 'New passwords do not match.'})
            
        # 3. The Magic Step: Find user and securely update password
        user = User.objects.get(email=email)
        user.set_password(new_password) # NEVER do user.password = new_password. Always use set_password() so it hashes securely!
        user.save()
        
        # 4. Clean up session
        del request.session['reset_email']
        del request.session['reset_otp']
        
        # Send them back to the login page so they can try their new password
        return redirect('login')

    return render(request, 'login/reset_password.html')