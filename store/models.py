from django.utils import timezone
import math
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from uuid import uuid4
from django.utils.text import slugify
from moviepy.editor import VideoFileClip



NOTI_TYPE = (
    ('New Order', 'New Order'),
    ('New Review', 'New Review'),
    ('New Course Question', 'New Course Question'),
    ('Course Published', 'Course Published'),
    ('Draft', 'Draft'),
    ('Course Enrollment Completed', 'Course Enrollment Completed'),
)


TEACHER_STATUS = (
    ('Draft', 'Draft'),
    ('Disabled', 'Disabled'),
    ('Published', 'Published'),
)


PLATFORM_STATUS = (
    ('Review', 'Review'),
    ('Disabled', 'Disabled'),
    ('Rejected', 'Rejected'),
    ('Draft', 'Draft'),
    ('Published', 'Published'),
)

LANGUAGE = (
    ('english', 'english'),
    ('Spanish', 'Spanish'),
    ('French', 'French'),
)

LEVEL = (
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
)

RATING = (
    (1, '1 Star'),
    (2, '2 Star'),
    (3, '3 Star'),
    (4, '4 Star'),
    (5, '5 Star'),
)



class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='course-file', default='category.jpg', blank=True, null=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'category'
        ordering = ['title']


    def __str__(self):
        return self.title    
    
    def course_count(self):
        return Course.objects.filter(category=self).count()
    
    def save(self, *args, **kwargs):
        if self.slug == '' or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)
    

    def __str__(self):
        return self.title

class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return f'{str(self.discount)} | {str(self.description)}'



class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.FileField(upload_to='course-file', blank=True, null=True, default='default.jpg')
    full_name = models.CharField(max_length=255)
    bio = models.CharField(max_length=255, blank=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.full_name
    
    def students(self):
        return OrderItem.objects.filter(teacher=self)
    
    def courses(self):
        return Course.objects.filter(teacher=self)
    
    def review(self):
        return Course.objects.filter(teacher=self).count()


class Course(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='courses')
    slug = models.SlugField()
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    file = models.FileField(upload_to='course-file', blank=True, null=True)
    image = models.FileField(upload_to='course-file', blank=True, null=True)
    language = models.CharField(max_length=255, choices=LANGUAGE, default='English')
    level = models.CharField(max_length=255, choices=LEVEL, default='Beginner')
    platform_status = models.CharField(max_length=255, choices=PLATFORM_STATUS, default='Published')
    teacher_course_status = models.CharField(max_length=255, choices=TEACHER_STATUS, default='Published')
    featured = models.BooleanField(default=False)
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    discounts = models.ManyToManyField(Discount, blank=True)

    def __str__(self):
        return self.name





class Variant(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
    def variant_items(self):
        return VariantItem.objects.filter(variant=self)


class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variant_items')
    title = models.CharField(max_length=1000)
    description = models.TextField()
    file = models.FileField(upload_to='course_file')
    duration = models.DurationField(blank=True, null=True)
    preview = models.BooleanField(default=False)
    content_duration = models.CharField(max_length=1000, blank=True)
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f'{self.variant.title} - {self.title}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file:
            """
              if there is clip file, this function calculate 
              the duration of the clip and then save it
            """
            clip = VideoFileClip(self.file.path)
            duration_seconds = clip.duration

            minutes, remainder = divmod(duration_seconds, 60)
            minutes = math.floor(minutes)
            seconds = math.floor(remainder)

            duration_text = f'{minutes} m {seconds} s'

            self.content_duration = duration_text
            super().save(update_fields=['content_duration'])


class Question_Answer(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=1000, blank=True)
    date = models.DateTimeField(default=timezone.now)   

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
    
    class Meta:
        ordering = ['-date']

    def messages(self):
        return Question_Answer_Message.objectd.filter(question=self)

    def profile(self):
        return Customer.objects.get(user=self.user)



class Question_Answer_Message(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(Question_Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
    
    class Meta:
        ordering = ['date']

    def profile(self):
        return Customer.objects.get(user=self.user)


class Question_Answer_Message(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(Question_Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    
    date = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
    
    class Meta:
        ordering = ['date']

    def profile(self):
        return Customer.objects.get(user=self.user)
    

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,)
    phone_number = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    image = models.FileField(upload_to='user_folder', default='default-user.jpg', null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    

    # @property
    # def full_name(self):
    #     return f'{self.user.first_name} {self.user.last_name}'
    
    # @property
    # def first_name(self):
    #     return self.user.first_name
    
    # @property
    # def last_name(self):
    #     return self.user.last_name

    class Meta:
        permissions = [
            ('send_private_email', 'can send private email touser by the button'),
        ]


class Address(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)


class UnpaidOrderManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=Order.ORDER_STATUS_UNPAID)
    
# class OrderManager(models.Manager):
#     def get_by_status(self, status):
#         if status in [Order.ORDER_STATUS_PAID, Order.ORDER_STATUS_UNPAID, Order.ORDER_STATUS_CANCELED]:
#             return super().get_queryset().filter(status=status)
#         return super().get_queryset()


class Order(models.Model):
    ORDER_STATUS_PAID = 'p'
    ORDER_STATUS_UNPAID = 'u'
    ORDER_STATUS_CANCELED = 'c'
    ORDER_STATUS = [
        (ORDER_STATUS_PAID,'Paid'),
        (ORDER_STATUS_UNPAID,'Unpaid'),
        (ORDER_STATUS_CANCELED,'Canceled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default=ORDER_STATUS_UNPAID)


    zarinpal_authority = models.CharField(max_length=255, blank=True)
    zarinpal_ref_id = models.CharField(max_length=150, blank=True)
    zarinpal_data = models.TextField(blank=True)


    objects = models.Manager()
    unpaid_orders = UnpaidOrderManager()

    def __str__(self):
        return f'Order id={self.id}'
    
    def get_total_price(self):
        total = sum([item.get_cost() for item in self.items.all()])
        return total
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='order_items')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = [['order', 'course']]

    def get_cost(self):
        return self.unit_price     

class CommentManager(models.Manager):
    def get_approved(self):
        return self.get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)

class ApprovedCommentManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)


class Comment(models.Model):
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_NOT_APPROVED = 'na'
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, 'Waiting'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    reply = models.CharField(max_length=1000, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=COMMENT_STATUS, default=COMMENT_STATUS_WAITING)

    objects = CommentManager()
    Approved = ApprovedCommentManager()

    

    


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cart_items')
    

    class Meta:
        unique_together = [['cart', 'course']]


class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.course.title
    

class CompletedLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    variant_item = models.ForeignKey(VariantItem, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title    
    
class EnrolledCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrolled')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title
    
    def letures(self):
        return VariantItem.objects.filter(variant__course=self.course)
    
    def completed_lesson(self):
        return CompletedLesson.objects.filter(course=self.course, user=self.user)
    
    def curriculum(self):
        return Variant.objects.filter(course=self.course)
    
    def note(self):
        return Note.objects.filter(course=self.course, user=self.user)
    
    def question_answer(self):
        return Question_Answer.objects.filter(course=self.course)
    
    def review(self):
        return Comment.objects.filter(course=self.course, user=self.user).first()    


class Note(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=1000, blank=True)
    note = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title    
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    review = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=255, choices=NOTI_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.type


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.user