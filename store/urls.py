from django.urls import include, path
# from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views

# urlpatterns = [
#    path('products/', views.ProductList.as_view()),
#    path('products/<int:pk>/', views.ProductDetail.as_view()),
#    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
#    path('categories/', views.CategoryList.as_view(), name='category-list'),

# ]
router = routers.DefaultRouter()
# router = SimpleRouter()
router.register('courses', views.CourseViewSet, basename='course') # product-list | product-detail
router.register('categories', views.CategoryViewSet, basename='category') # category-list | category-detail
router.register('carts', views.CartViewSet, basename='cart')
router.register('customers', views.CustomerViewSet, basename='customer')
router.register('orders', views.OrderViewSet, basename='order')

#-------------for showing comments of special product
courses_router = routers.NestedDefaultRouter(router, 'courses', lookup='course')
courses_router.register('comments', views.CommentViewSet, basename='course-comments')


cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + courses_router.urls + cart_items_router.urls
