from django.urls import path
from . import views
urlpatterns=[
    path('products/',views.ProductListviews.as_view()),
    path('review/<str:uuid>',views.ReviewListView.as_view()),
    path('createreview/',views.ReviewCreateView.as_view())
]