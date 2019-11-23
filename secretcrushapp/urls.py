from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loginView, name='login'),
    path('signup/', views.signupView, name='signup'),
    path('account/', views.accountView, name='account'),
    path('account/edit/', views.accountEditView, name='accountEdit'),
    path('account/change_password/', views.changePasswordView, name='changePassword'),
    path('account/change_password/done', views.changePasswordDoneView, name='changePasswordDone'),
    path('reset_password/', views.resetPasswordView, name='resetPassword'),
    path('reset_password_done/', views.resetPasswordDoneView, name='resetPasswordDone'),
    path('confirm_reset_password/<uidb64>/<token>/', views.confirmResetPasswordView, name='confirmResetPassword'),
    path('complete_reset_password/', views.completeResetPasswordView, name='completeResetPassword'),
    path('account/instagram/link/', views.linkInstagramView, name='linkInstagram'),
    path('account/instagram/auth/', views.authInstagramView, name='authInstagram'),
    path('logout/', views.logoutView, name='logout'),
]