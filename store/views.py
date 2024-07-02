from django.shortcuts import get_object_or_404
from django.db.models import Count, Prefetch

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet 
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny 
#ReadOnlyModelViewSet   instead of     ModelViewSet | for only read and get objects without deleting and updating
from django_filters.rest_framework import DjangoFilterBackend
from store.models import Cart, CartItem, Category, Comment, Course, Customer, Order, OrderItem
from store.paginations import DefaultPagination
from store.permissions import CustomDjangoModelPermissions, IsAdminOrReadOnly, SendPrivateEmailToCustomerPermission
from store.serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CategorySerializer, CommentSerializer, CourseSerializer, CustomerSerializer, OrderCreateSerializer, OrderForAdminSerializer, OrderSerializer, OrderUpdateSerializer, UpdateCartItemSerializer

from .signals import order_created




#class-based view
#productlist and product detail both together including post put patch delete-------------------------------------------------
class CourseViewSet(ModelViewSet):

     serializer_class = CourseSerializer
     filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
     ordering_fields = ['name', 'unit_price']
     search_fields = ['name', 'category__title']
     #----custom pagination----
     # pagination_class = DefaultPagination
     #-------------------------
     # filterset_fields = ['category_id', 'inventory']
     
     permission_classes = [IsAdminOrReadOnly]
     queryset = Course.objects.all()
      
     def get_serializer_context(self):
          return {'request': self.request}
     
     def destroy(self, request, pk):
          course = get_object_or_404(Course.objects.select_related('category'), pk=pk)
          if course.order_items.count() > 0:
              return Response({'error': 'there is some orderitems including this course'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
          course.delete()
          return Response(status=status.HTTP_204_NO_CONTENT)
#--------------------------------------------------------------------------------------------------




# class ProductList(ListCreateAPIView):

#      serializer_class = ProductSerializer
#      queryset = Product.objects.select_related('category').all()

     # def get_serializer_class(self):
     #      return ProductSerializer
     
     # def get_queryset(self):
     #      return Product.objects.select_related('category').all()
     
     # def get_serializer_context(self):
     #      return {'request': self.request}




# class ProductList(APIView):

#      def get(self,request):
#           products_queryset = Product.objects.select_related('category').all()
#           serializer = ProductSerializer(products_queryset,context={'request': request}, many=True)
#           return Response(serializer.data)
     
#      def post(self, request):
#           serializer = ProductSerializer(data=request.data)
#           serializer.is_valid(raise_exception=True)
#           serializer.save()
#           return Response(serializer.data, status=status.HTTP_201_CREATED)



#functionalview
# @api_view(['GET', 'POST'])
# def product_list(request):
#      if request.method == 'GET':
#             products_queryset = Product.objects.select_related('category').all()
#             serializer = ProductSerializer(products_queryset,context={'request': request}, many=True)
#             return Response(serializer.data)
     

#      elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#class-based view
# class ProductDetail(RetrieveUpdateDestroyAPIView):

#      serializer_class = ProductSerializer
#      queryset = Product.objects.select_related('category')


#      def delete(self, request, pk):
#           product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
#           if product.order_items.count() > 0:
#               return Response({'error': 'there is some orderitems including this product'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#           product.delete()
#           return Response(status=status.HTTP_204_NO_CONTENT)



# class ProductDetail(APIView):
#      def get(self, request, pk):
          
#           product = get_object_or_404(Product.objects.select_related('category'), pk=pk) 
#           serializer = ProductSerializer(product, context={'request': request})
#           return Response(serializer.data)

#      def put(self, request, pk):
#           product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
#           serializer = ProductSerializer(product, data=request.data)
#           serializer.is_valid(raise_exception=True)
#           serializer.save()
#           return Response(serializer.data)

#      def delete(self, request, pk):
#           product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
#           if product.order_items.count() > 0:
#               return Response({'error': 'there is some orderitems including this product'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#           product.delete()
#           return Response(status=status.HTTP_204_NO_CONTENT)




#functional view
# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail(request, pk):
#     product = get_object_or_404(Product.objects.select_related('category'), pk=pk)   

#     if request.method == 'GET':
#         serializer = ProductSerializer(product, context={'request': request})
#         return Response(serializer.data)
    
#     elif request.method == 'PUT':
#          serializer = ProductSerializer(product, data=request.data)
#          serializer.is_valid(raise_exception=True)
#          serializer.save()
#          return Response(serializer.data)
    
#     elif request.method == 'DELETE':
#          if product.order_items.count() > 0:
#               return Response({'error': 'there is some orderitems including this product'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#          product.delete()
#          return Response(status=status.HTTP_204_NO_CONTENT)
    


         
   
    # if serializer.is_valid():
    #     serializer.validated_data
    #     return Response('everything is ok')

    # else:
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # return Response('All ok')

#category list and category detail both together-------------------------------------------------------
class CategoryViewSet(ModelViewSet):
     serializer_class = CategorySerializer
     queryset = Category.objects.prefetch_related('courses').all()
     permission_classes = [IsAdminOrReadOnly]


     def destroy(self, request, pk):
          category = get_object_or_404(Category.objects.prefetch_related('courses'), pk=pk)
          if category.courses.count() > 0:
              return Response({'error': 'there is some courses related to this category'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
              
          category.delete()
          return Response(status=status.HTTP_204_NO_CONTENT)
#-------------------------------------------------------------------------------------------------------




# class CategoryList(ListCreateAPIView):
#      serializer_class = CategorySerializer
#      queryset = Category.objects.prefetch_related('products').all()


# class CategoryList(APIView):

#      def get(self, request):
#           categories_queryset = Category.objects.prefetch_related('products').all()
#           serializer = CategorySerializer(categories_queryset, many=True)
#           return Response(serializer.data)
     
#      def post(self, request):
#           serializer = CategorySerializer(data=request.data)
#           serializer.is_valid(raise_exception=True)
#           serializer.save()
#           return Response(serializer.data, status=status.HTTP_201_CREATED)





#functional view    
# @api_view(['GET', 'POST'])
# def category_list(request):
#      if request.method == 'GET':
#           categories_queryset = Category.objects.annotate(products_count=Count('products')).all()
#           serializer = CategorySerializer(categories_queryset, many=True)
#           return Response(serializer.data)
     
#      elif request.method == 'POST':
#         serializer = CategorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)



# class CategoryDetail(RetrieveUpdateDestroyAPIView):
#      serializer_class = CategorySerializer
#      queryset = Category.objects.prefetch_related('products')


#      def delete(self, request, pk):
#           category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
#           if category.products.count() > 0:
#               return Response({'error': 'there is some products related to this category'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
              
#           category.delete()
#           return Response(status=status.HTTP_204_NO_CONTENT)




# class CategoryDetail(APIView):
#      def get(self, request, pk):
#           category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
#           serializer = CategorySerializer(category)
#           return Response(serializer.data)
     
#      def put(self, request, pk):
#           category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
#           serializer = CategorySerializer(category, data=request.data)
#           serializer.is_valid(raise_exception=True)
#           serializer.save()
#           return Response(serializer.data)
     
#      def delete(self, request, pk):
#           category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
#           if category.products.count() > 0:
#               return Response({'error': 'there is some products related to this category'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
              
#           category.delete()
#           return Response(status=status.HTTP_204_NO_CONTENT)






# @api_view(['GET', 'PUT', 'DELETE'])
# def category_detail(request, pk):
#     category = get_object_or_404(Category.objects.annotate(products_count=Count('products')), pk=pk)
#     if request.method == 'GET':
#         serializer = CategorySerializer(category)
#         return Response(serializer.data)
    
#     elif request.method == 'PUT':
#          serializer = CategorySerializer(category, data=request.data)
#          serializer.is_valid(raise_exception=True)
#          serializer.save()
#          return Response(serializer.data)
    
#     elif request.method == 'DELETE':
#          if category.products.count() > 0:
#               return Response({'error': 'there is some products related to this category'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
              
#          category.delete()
#          return Response(status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(ModelViewSet):
     serializer_class = CommentSerializer

     def get_queryset(self):
          course_pk = self.kwargs['product_pk']
          return Comment.objects.filter(course_id=course_pk).all()
     
     def get_serializer_context(self):
          return{'course_pk': self.kwargs['course_pk']}


class CartItemViewSet(ModelViewSet):
     http_method_names = ['get', 'post', 'patch', 'delete']

     
     def get_queryset(self):
          cart_pk = self.kwargs['cart_pk']
          return CartItem.objects.select_related('course').filter(cart_id=cart_pk).all()


     def get_serializer_class(self):
          if self.request.method == 'POST':
               return AddCartItemSerializer
          elif self.request.method == 'PATCH':
               return UpdateCartItemSerializer
          return CartItemSerializer
     
     def get_serializer_context(self):
          return{'cart_pk': self.kwargs['cart_pk']}


class CartViewSet(CreateModelMixin,
                   RetrieveModelMixin,
                   DestroyModelMixin,
                   GenericViewSet):
     serializer_class = CartSerializer
     queryset = Cart.objects.prefetch_related('items__course').all()
     lookup_value_regex = '[0-9a-fA-F]{8}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{12}'

class CustomerViewSet(ModelViewSet):
     serializer_class = CustomerSerializer   
     queryset = Customer.objects.all()
     permission_classes = [IsAdminUser]

     @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
     def me(self, request):
          user_id = request.user.id
          customer = Customer.objects.get(user_id=user_id)
          if request.method == 'GET':
              serializer = CustomerSerializer(customer)
              return Response(serializer.data)
          elif request.method == 'PUT':
               serializer = CustomerSerializer(customer, data=request.data)
               serializer.is_valid(raise_exception=True)
               serializer.save()
               return Response(serializer.data)
          

     @action(detail=True, permission_classes=[SendPrivateEmailToCustomerPermission])
     def send_private_email(self, request, pk):
          return Response(f'Sending email to customer {pk=}')



class OrderViewSet(ModelViewSet):

     http_method_names = ['get', 'post', 'delete', 'patch', 'options','head']
     
     def get_permissions(self):
          if self.request.method in ['PATCH', 'DELETE']:
               return [IsAdminUser()]
          return [IsAuthenticated()]
          

     def get_queryset(self):
          queryset = Order.objects.prefetch_related(
               Prefetch(
                    'items', queryset=OrderItem.objects.select_related('course'),
                    )
          ).select_related('customer__user').all()
          
          user = self.request.user

          if user.is_staff:
               return queryset
          
          return queryset.filter(customer__user_id=user.id)
     

     def get_serializer_class(self):
          if self.request.method == 'POST':
               return OrderCreateSerializer
          
          if self.request.method == 'PATCH':
               return OrderUpdateSerializer
          
          if self.request.user.is_staff:
               return OrderForAdminSerializer
          return OrderSerializer 

          


     
     def get_serializer_context(self):
          return {'user_id': self.request.user.id}
     

     def create(self, request, *args, **kwargs):
          create_order_serializer  = OrderCreateSerializer(data=request.data,
                       context={'user_id': self.request.user.id},                                    
                    )
          create_order_serializer.is_valid(raise_exception=True)
          created_order = create_order_serializer.save()

          order_created.send_robust(self.__class__, order=created_order)

          serializer= OrderSerializer(created_order)
          return Response(serializer.data)

          