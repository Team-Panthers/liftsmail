# from dj_rest_auth.registration.views import RegisterView, VerifyEmailView, ResendEmailVerificationView
# from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import path,include
# from users.views import email_confirm_redirect, password_reset_confirm_redirect


urlpatterns = [
    
    
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path("", include("djoser.social.urls")),
    
    
    
    
    # path("register/", RegisterView.as_view(), name="rest_register"),
    
    # path('account-email-verification-sent/', VerifyEmailView.as_view(),name='account_email_verification_sent'),
    # path("account-confirm-email/<str:key>/", email_confirm_redirect, name="account_confirm_email"),
    # path("register/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    # path("register/resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"),

    # path("login/", LoginView.as_view(), name="rest_login"),
    # path("logout/", LogoutView.as_view(), name="rest_logout"),
    # path("user/", UserDetailsView.as_view(), name="rest_user_details"),

    # path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    # path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    # path("password/reset/confirm/<str:uidb64>/<str:token>/", password_reset_confirm_redirect,name="password_reset_confirm"),
    # path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]