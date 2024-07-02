from django.urls import include, path
# from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views


app_name = 'store'
router = routers.DefaultRouter()
# router = SimpleRouter()
router.register('courses', views.CourseViewSet, basename='course') 
router.register('categories', views.CategoryViewSet, basename='category') 
router.register('carts', views.CartViewSet, basename='cart')
router.register('customers', views.CustomerViewSet, basename='customer')
router.register('orders', views.OrderViewSet, basename='order')


courses_router = routers.NestedDefaultRouter(router, 'courses', lookup='course')
courses_router.register('comments', views.CommentViewSet, basename='course-comments')


cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [

    path('orders/<int:order_id>/pay/', views.OrderPayView.as_view(), name='order-pay'),
    path('orders/verify', views.OrderVerifyView.as_view(), name='order_verify')

] + router.urls + courses_router.urls + cart_items_router.urls
