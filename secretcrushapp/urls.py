from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loginView, name='login'),
    path('signup/', views.signupView, name='signup'),
    path('crushes/', views.crushListView, name='crushList'),
    path('match/', views.matchView, name='match'),
    path('account/', views.accountView, name='account'),
    path('account/edit/', views.accountEditView, name='accountEdit'),
    path('account/delete/', views.accountDeleteView, name='accountDelete'),
    path('account/password/change/', views.changePasswordView, name='changePassword'),
    path('account/password/change/done/', views.changePasswordDoneView, name='changePasswordDone'),
    path('password/reset/', views.resetPasswordView, name='resetPassword'),
    path('password/reset/done/', views.resetPasswordDoneView, name='resetPasswordDone'),
    path('password/reset/confirm/<uidb64>/<token>/', views.confirmResetPasswordView, name='confirmResetPassword'),
    path('password/reset/complete/', views.completeResetPasswordView, name='completeResetPassword'),
    path('account/instagram/link/', views.linkInstagramView, name='linkInstagram'),
    path('account/instagram/auth/', views.authInstagramView, name='authInstagram'),
    path('account/instagram/remove/confirm/', views.removeInstagramConfirmview, name='removeInstagramConfirm'),
    path('account/instagram/remove/', views.removeInstagramView, name='removeInstagram'),
    path('crush/addnew/', views.addCrushView, name='addCrush'),
    path('crush/edit/<crushUsername>/', views.editCrushView, name='editCrush'),
    path('crush/delete/<crushUsername>/', views.deleteCrushView, name='deleteCrush'),
    path('logout/', views.logoutView, name='logout'),
    path('privacy/', views.privacyView, name='privacy'),
    path('terms/', views.termsView, name='terms'),
    path('howitworks/', views.howitworksView, name='howitworks'),
    path('faq/', views.faqView, name='faq'),
    path('contactus/', views.contactusView, name='contactUs'),
    path('about/', views.aboutView, name='about'),
]