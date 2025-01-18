from django.urls import path
from . import views
urlpatterns=[
    path('products/',views.ProductListvie.as_view()),
    path('review/<str:uuid>',views.ReviewListVie.as_view()),
    path('createreview/',views.ReviewCreateVie.as_view())
]
