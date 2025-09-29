from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    # Standard JWT endpoints
    path('api/auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Custom auth endpoints
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/register/', views.register_view, name='register'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('api/auth/profile/', views.profile_view, name='profile'),
    path('api/auth/profile/update/', views.update_profile_view, name='update_profile'),
    path('api/auth/password/change/', views.change_password_view, name='change_password'),
    path('api/auth/password/request-reset/', views.password_reset_request, name='password_reset_request'),
    path('api/auth/password/reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Google OAuth
    path('api/auth/google/', views.google_auth_url, name='google_auth_url'),
    path('api/auth/google/callback/', views.google_auth_callback, name='google_auth_callback'),
    
    # GitHub OAuth
    path('api/auth/github/', views.github_auth_url, name='github_auth_url'),
    path('api/auth/github/callback/', views.github_auth_callback, name='github_auth_callback'),
    
    # User CRUD operations
    path('api/', include(router.urls)),
]