from decimal import Decimal
from rest_framework import serializers
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.db import transaction
from store.models import Cart, CartItem, Category, Certificate, CompletedLesson, Customer, EnrolledCourse, Note, Notification, Order, OrderItem, Course, Comment, Question_Answer, Question_Answer_Message, Teacher, Variant, VariantItem, Wishlist


# DOLLORS_TO_RIALS = 500000
TAX = 1.09

class CategorySerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Category
        fields = ['id', 'title', 'image','slug']

    # def get_num_of_products(self, category):
    #     return category.products.count()


class VariantItemSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = VariantItem
        fields = '__all__' 


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'name', 'body', 'rating', 'reply']

    def create(self, validated_data):
        course_id = self.context['course_pk']
        return Comment.objects.create(course_id=course_id, **validated_data)  


class CompletedLessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompletedLesson
        fields = '__all__' 



class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = '__all__' 



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'birth_date']
        read_only_fields = ['user']


class Question_Answer_MessageSerializer(serializers.ModelSerializer):
    profile = CustomerSerializer(many=False)
    class Meta:
        model = Question_Answer_Message
        fields = '__all__'                 




class Question_AnswerSerializer(serializers.ModelSerializer):
    messages = Question_Answer_MessageSerializer(many=True)
    profile = CustomerSerializer(many=False)

    class Meta:
        model = Question_Answer
        fields = '__all__'   



class EnrolledCourseSerializer(serializers.ModelSerializer):
    letures = VariantItemSerializer(many=True, read_only=True)
    completed_lesson = CompletedLessonSerializer(many=True, read_only=True)
    curriculum = VariantItemSerializer(many=True, read_only=True)
    note = NoteSerializer(many=True, read_only=True)
    question_answer = Question_AnswerSerializer(many=True, read_only=True)
    comment= CommentSerializer(many=True, read_only=True)

    class Meta:
        model = EnrolledCourse
        fields = '__all__'



class CourseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, source='name')
    price = serializers.DecimalField(max_digits=255, decimal_places=2, source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    students = EnrolledCourseSerializer(many=True, read_only=True)
    curiculum = VariantItemSerializer(many=True, read_only=True)
    lectures = VariantItemSerializer(many=True, read_only=True)
    # category = CategorySerializer()
    # category = serializers.HyperlinkedRelatedField(
    #     queryset = Category.objects.all(),
    #     view_name='category-detail',
    # )

    class Meta:
        model = Course
        fields = ['id', 'title', 'price','price_with_tax', 'category', 'description', 'teacher', 'file', 'image', 'language', 'level', 'platform_status','curiculum' , 'students', 'lectures', 'teacher_course_status', 'featured', 'datetime_created']



    def calculate_tax(self, course):
        return round(course.unit_price * Decimal(TAX), 2)

    #extra validation for is_valid method
    def validate(self, data):
        if  len(data['name']) < 6:
            raise serializers.ValidationError('course title should be at least 6 characters')
        return data

    def create(self, validated_data):
        course = Course(**validated_data)
        course.slug = slugify(course.name)
        course.save()
        return course


    # def update(self, instance, validated_data):
    #     instance.inventory= validated_data.get('inventory')
    #     instance.save()
    #     return instance
        



#روش اول
# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField(max_length=255)
#     unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
#     inventory = serializers.IntegerField(validators=[MinValueValidator(0)])
#     #category = serializers.StringRelatedField()
#     # category = CategorySerializer()
#     category = serializers.HyperlinkedRelatedField(
#         queryset = Category.objects.all(),
#         view_name='category-detail',
#     )
    # price_rial = serializers.SerializerMethodField()


    # def get_price_rial(self, product):
    #     return int(product.unit_price * DOLLORS_TO_RIALS)

  


class CartCourseSerializer(serializers.ModelSerializer):

    class Meta:
        model= Course
        fields = ['id', 'name', 'unit_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['course']



class AddCartItemSerializer(serializers.ModelSerializer):

    class Meta: 
        model = CartItem
        fields = ['id', 'course']

    def create(self, validated_data):
        cart_id = self.context['cart_pk']

        course = validated_data.get('course')
        

        try:
            cart_item =CartItem.objects.get(cart_id=cart_id, course_id=course.id)
            
            cart_item.save()

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)

        self.instance = cart_item
        return cart_item   


class CartItemSerializer(serializers.ModelSerializer):
    course = CartCourseSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'course']

    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

   
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        read_only_fields= ['id']

    def get_total_price(self, cart):
       return sum([item.course.unit_price for item in cart.items.all()])
    



class OrderCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields =['id', 'name', 'unit_price']



class OrderCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, source='user.first_name')
    last_name = serializers.CharField(max_length=255, source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email']



class OrderItemSerializer(serializers.ModelSerializer):
    course = OrderCourseSerializer()
    class Meta:
         model = OrderItem
         fields = ['id', 'course', 'unit_price']



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'datetime_created', 'items' ]




class OrderForAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = OrderCustomerSerializer()
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'datetime_created', 'items' ]


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']




class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        # try:
        #     if Cart.objects.prefetch_related('items').get(id=cart_id).items.coount() == 0:
        #         raise serializers.ValidationError('Your cart is empty.Please add some products')
        # except Cart.DoesNotExist:
        #     raise serializers.ValidationError('There is no cart with this cart id !')  


         if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('There is no cart with this cart id')

         if CartItem.objects.filter(cart_id=cart_id).count() == 0:
             raise serializers.ValidationError('Your cart is empty, please add some courses')
         return cart_id
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)

            order = Order()
            order.customer = customer
            order.save()

            cart_items = CartItem.objects.select_related('course').filter(cart_id=cart_id)

            order_items = [
                OrderItem(
                    order=order,
                    course=cart_item.course,
                    unit_price=cart_item.course.unit_price,
                    teacher=cart_item.course.teacher,
                ) for cart_item in cart_items
            ]


            # order_items = list()
            # for cart_item in cart_items:
            #     order_item = OrderItem()
            #     order_item.order= order
            #     order_item.product_id = cart_item.product_id
            #     order_item.unit_price = cart_item.product.unit_price
            #     order_item.quantity = cart_item.quantity

            #     order_items.append(order_item)

            OrderItem.objects.bulk_create(order_items)   

            Cart.objects.get(id=cart_id).delete()

            return order

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ['user', 'image', 'full_name', 'bio', 'facebook', 'twitter', 'about', 'country', 'students', 'courses', 'review']        
            


class VariantSerializer(serializers.ModelSerializer):
    variant_items = VariantItemSerializer(many=True)

    class Meta:
        model = Variant
        fields = '__all__'         


class CertificateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Certificate
        fields = '__all__'           

          

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'           


class WishlistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wishlist
        fields = '__all__'           


class StudentSummarySerializer(serializers.Serializer):
    total_courses = serializers.IntegerField(default=0)
    completed_lessons = serializers.IntegerField(default=0)
    achieved_certificates = serializers.IntegerField(default=0)
    