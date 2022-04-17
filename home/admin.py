from django.contrib import admin
from .models import Product,Category,SubCategory,Customer,Order



class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 3


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','parent']
    list_editable = ['parent',]
    fieldsets = (
        (
            None,{
                'fields':('name',)
            }
        ),
    )
    inlines = (SubCategoryInline,)

class ProductInline(admin.TabularInline):
    model = Product
    extra = 3

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name','parent','product_count']

    fieldsets = (
        (
            None,{
                'fields':('name',)
            }
        ),
    )
    inlines = (ProductInline,)

    def product_count(self,obj):
        return obj.product_set.count()

    def get_ordering(self,request):
        return ('parent','name')


admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory,SubCategoryAdmin)
admin.site.register(Customer)
admin.site.register(Order)

