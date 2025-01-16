# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('user/<int:id>',views.UserDetailView.as_view()),
    path('signup/',views.UserCreateView.as_view()),
    path('login/',views.UserLoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('mobile-validate/',views.mobileValidateView.as_view()),
    path('otp-validate/',views.OTPValidateView.as_view()),
    path('changepassword/',views.ChangePasswordView.as_view()),
    path('user/update/',views.UserUpdateView.as_view()),
    path('create-order/', views.CreateOrderView.as_view()),
    path('order-Update/<uuid:uuid>/', views.OrderUpdateView.as_view()),      
    path('ordersItem/<int:user_id>/',views.UserOrderDetailView.as_view()),
    path('create-checkout-session/',views.StripeCheckoutViews.as_view()),
]
