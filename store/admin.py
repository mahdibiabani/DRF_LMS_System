from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode



from .models import Cart, CartItem, Category, Certificate, CompletedLesson, Course, Customer, EnrolledCourse, Note, Notification, Order, OrderItem, Comment, Question_Answer, Question_Answer_Message, Teacher, Variant, VariantItem, Wishlist


                

class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit_price','teacher','language','image','level', 'course_category', 'num_of_comments']
    list_per_page = 10
    list_editable = ['unit_price']
    list_select_related = ['category']
    list_filter = ['datetime_created', ]
    search_fields = ['name']
    # fields = []فیلدهایی که میخواهید نمایش دهید
    # exclude = []فیلد هایی که میخوهید نمایش داده نشوند
    # readonly_fields = [] فیلد هایی که میخواهیم فقط نمایش داده شوند و قابل تغییر نباشند
    prepopulated_fields = {
        'slug': ['name', ]
    }


    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('comments').annotate(comments_count=Count('comments'))


    @admin.display(description='# comments', ordering='comments_count')
    def num_of_comments(self,course):
        url = (
            reverse('admin:store_comment_changelist')
            + '?'
            + urlencode({
                'course__id': course.id,
            })
        )
        return format_html('<a href="{}">{}</a>', url, course.comments_count)
        # return product.comments_count


    

    @admin.display(ordering='category_id')
    def course_category(self, course):
        return course.category.title


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['course','teacher', 'unit_price']
    extra = 0
    min_num = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status','datetime_created', 'num_of_items']
    list_editable = ['status']
    list_per_page = 5
    ordering = ['-datetime_created',]
    inlines =[OrderItemInline]


    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).prefetch_related('items').annotate(items_count=Count('items'))


    @admin.display(ordering='items_count', description='# items')
    def num_of_items(self, order):
        return order.items_count

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'status']
    list_editable = ['status']
    list_per_page = 10
    list_display_links = ['course']
    autocomplete_fields = ['course']


admin.site.register(Course, CourseAdmin)
admin.site.register(Category)
admin.site.register(Order, OrderAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Teacher)
admin.site.register(VariantItem)
admin.site.register(Question_Answer)
admin.site.register(Question_Answer_Message)
admin.site.register(Certificate)
admin.site.register(CompletedLesson)
admin.site.register(EnrolledCourse)
admin.site.register(Note)
admin.site.register(Notification)
admin.site.register(Wishlist)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    list_per_page = 10
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']

    def first_name(self, customer):
        return customer.user.first_name

    def last_name(self, customer):
        return customer.user.last_name
    
    def email(self, customer):
        return customer.user.email



@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'course', 'unit_price']  
    list_per_page = 10
    autocomplete_fields = ['course']


class CartItemInline(admin.TabularInline):
    model =  CartItem
    fields = ['id', 'course']
    extra = 0
    min_num = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    inlines = [CartItemInline]



class VariantItemInline(admin.TabularInline):
    model = VariantItem
    fields = ['title', 'file', 'duration']   

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    model = Variant
    inlines = [VariantItemInline]    