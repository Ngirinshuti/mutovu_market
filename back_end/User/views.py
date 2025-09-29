from User.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from User.serializers import UserSerializer, UserRegistrationSerializer, UserProfileSerializer, PasswordChangeSerializer
from User.serializers import EmailSerializer, SetNewPasswordSerializer 
from django.conf import settings
import requests
import secrets
import string


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [permission() for permission in self.permission_classes]
        return []
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return JsonResponse({'message':'User created successfully', 'data': serializer.data}, status=201)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return JsonResponse({'message':'User updated successfully', 'data': serializer.data}, status=200)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return JsonResponse({'message': 'User deleted successfully'}, status=204)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username')
            user = User.objects.get(username=username)
            user_data = UserProfileSerializer(user).data
            response.data['user'] = user_data
        return response

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'message': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        
        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'message': 'Registration successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Registration failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def google_auth_url(request):
    """Generate Google OAuth URL"""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.GOOGLE_OAUTH2_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_OAUTH2_REDIRECT_URI}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return Response({'auth_url': google_auth_url})

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth_callback(request):
    """Handle Google OAuth callback"""
    code = request.data.get('code')
    
    if not code:
        return Response({
            'message': 'Authorization code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Exchange code for tokens
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info from Google
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={tokens['access_token']}"
        user_response = requests.get(user_info_url)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Create or get user
        email = user_info.get('email')
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'is_verified': True,
            }
        )
        
        if created:
            # Generate random password for OAuth users
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            user.set_password(password)
            user.save()
        
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'message': 'Google authentication successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except requests.RequestException as e:
        return Response({
            'message': 'Google authentication failed',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def github_auth_url(request):
    """Generate GitHub OAuth URL"""
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={settings.GITHUB_CLIENT_ID}&"
        f"redirect_uri={settings.GITHUB_REDIRECT_URI}&"
        f"scope=user:email"
    )
    return Response({'auth_url': github_auth_url})

@api_view(['POST'])
@permission_classes([AllowAny])
def github_auth_callback(request):
    """Handle GitHub OAuth callback"""
    code = request.data.get('code')
    
    if not code:
        return Response({
            'message': 'Authorization code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Exchange code for access token
    token_url = 'https://github.com/login/oauth/access_token'
    token_data = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'code': code,
        # 🔑 CRITICAL FIX: Add redirect_uri to the token exchange payload
        'redirect_uri': settings.GITHUB_REDIRECT_URI, 
    }
    
    try:
        token_response = requests.post(
            token_url, 
            data=token_data,
            headers={'Accept': 'application/json'}
        )
        
        # 🐛 IMPROVED DEBUGGING: Check for the 400 error status before raising
        if token_response.status_code >= 400:
            print("--- GITHUB TOKEN EXCHANGE ERROR ---")
            print("Status Code:", token_response.status_code)
            try:
                # GitHub often sends the specific error in JSON format
                print("Error Response Body:", token_response.json())
            except requests.exceptions.JSONDecodeError:
                # Fallback to plain text if not JSON (less common for 400s)
                print("Error Response Text:", token_response.text)
            print("-----------------------------------")
        
        token_response.raise_for_status() # Raises the 400 if it was still an issue
        tokens = token_response.json()
        access_token = tokens.get('access_token')
        
        # ... (rest of the successful logic remains the same)
        # ...
        
        # Get user info from GitHub
        user_response = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {access_token}'}
        )
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # ... (rest of the user email and creation logic)
        
        # Get user emails (GitHub requires separate API call for emails)
        email_response = requests.get(
            'https://api.github.com/user/emails',
            headers={'Authorization': f'token {access_token}'}
        )
        email_response.raise_for_status()
        emails = email_response.json()
        
        primary_email = None
        for email_obj in emails:
            if email_obj.get('primary'):
                primary_email = email_obj.get('email')
                break
        
        if not primary_email:
            return Response({
                'message': 'No primary email found in GitHub account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=primary_email,
            defaults={
                'username': user_info.get('login', primary_email),
                'first_name': user_info.get('name', '').split(' ')[0] if user_info.get('name') else '',
                'last_name': ' '.join(user_info.get('name', '').split(' ')[1:]) if user_info.get('name') and len(user_info.get('name', '').split(' ')) > 1 else '',
                'bio': user_info.get('bio', ''),
                'is_verified': True,
            }
        )
        
        if created:
            # Generate random password for OAuth users
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            user.set_password(password)
            user.save()
        
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'message': 'GitHub authentication successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_200_OK)

    except requests.RequestException as e:
        # If the specific error wasn't caught above, return a general message
        return Response({
            'message': 'GitHub authentication failed',
            'error': f"Request error: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user_data = UserProfileSerializer(request.user).data
    return Response({'user': user_data}, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    serializer = UserProfileSerializer(request.user, data=request.data, partial=request.method == 'PATCH')
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Profile update failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Password change failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
    
# --- New Password Reset Request View ---
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Handles the request to start the password reset process (send email)."""
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Return a success message even if the user doesn't exist to prevent email enumeration
        return Response({'message': 'If an account with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)

    # 1. Generate UID (User ID) and Token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # 2. Construct Reset URL (Frontend URL)
    # NOTE: You MUST set FRONTEND_URL in your settings.py (see section D)
    # The frontend will handle the routing to the confirmation page:
    # /pages/auth/reset-password/[uid]/[token]
    reset_url = f"{settings.FRONTEND_URL}/pages/auth/reset-password/{uid}/{token}"

    # 3. Send Email
    email_body = f"""
    Hello {user.username},

    You requested a password reset for your account. 
    Please use the link below to set a new password:

    {reset_url}

    This link will expire soon. If you didn't request this, please ignore this email.

    Thank you,
    The Team
    """
    try:
        send_mail(
            'Password Reset Request',
            email_body,
            settings.DEFAULT_FROM_EMAIL, # Must be set in settings.py
            [user.email],
            fail_silently=False,
        )
        
    except Exception as e:
        # Log the actual email error for debugging
        print(f"Error sending email: {e}")
        return Response({'message': 'Email sending failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    return Response({'message': 'A password reset link has been sent to your email.'}, status=status.HTTP_200_OK)


# --- New Password Reset Confirmation View ---
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Handles the final confirmation of the password reset (set new password)."""
    serializer = SetNewPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    uidb64 = serializer.validated_data['uid']
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    try:
        # Decode the UID to get the user's primary key
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check if the user exists and the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successful. You can now log in with your new password.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Password reset link is invalid or has expired.'}, status=status.HTTP_400_BAD_REQUEST)
