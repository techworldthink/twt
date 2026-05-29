from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Management Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/products/add/', views.admin_product_create, name='admin_product_create'),
    path('dashboard/products/edit/<int:id>/', views.admin_product_edit, name='admin_product_edit'),
    path('dashboard/products/delete/<int:id>/', views.admin_product_delete, name='admin_product_delete'),
    path('dashboard/categories/', views.admin_categories, name='admin_categories'),
    path('dashboard/categories/add/', views.admin_category_create, name='admin_category_create'),
    path('dashboard/categories/edit/<int:id>/', views.admin_category_edit, name='admin_category_edit'),
    path('dashboard/categories/delete/<int:id>/', views.admin_category_delete, name='admin_category_delete'),
    path('dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('dashboard/orders/<int:id>/', views.admin_order_detail, name='admin_order_detail'),
    path('dashboard/orders/<int:id>/toggle-paid/', views.admin_order_toggle_paid, name='admin_order_toggle_paid'),
    path('dashboard/orders/<int:id>/status/', views.admin_order_update_status, name='admin_order_update_status'),
    path('dashboard/suppliers/', views.admin_suppliers, name='admin_suppliers'),
    path('dashboard/suppliers/add/', views.admin_supplier_create, name='admin_supplier_create'),
    path('dashboard/purchases/', views.admin_purchases, name='admin_purchases'),
    path('dashboard/purchases/add/', views.admin_purchase_create, name='admin_purchase_create'),
    path('dashboard/reports/', views.admin_reports, name='admin_reports'),
    
    # Cart and Order URLs
    path('cart/detail/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('order/create/', views.order_create, name='order_create'),
    
    # Homepage and dynamic slugs
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]
