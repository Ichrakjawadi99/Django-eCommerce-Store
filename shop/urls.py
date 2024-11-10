from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.shop, name='shop'),  # Renamed from 'shop/'
    path('products/<slug:category_slug>/', views.shop, name='categories'),  # Corrected typo
    path('products/<slug:category_slug>/<slug:product_details_slug>/', views.product_details, name='product_details'),
    path('search/', views.search, name='search'),
    path('review/<int:product_id>/', views.review, name='review'),
]
