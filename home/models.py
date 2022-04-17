
from django.db import models
from .managers import CategoryManager,SubCategoryManager
import  re,datetime
class Node(models.Model):
    name=models.CharField(max_length=150)
    parent=models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
    class Meta:
        ordering=('name',)


class Category(Node):
    objects=CategoryManager()
    class Meta:
        proxy=True

class SubCategory(Node):
    objects=SubCategoryManager()
    class Meta:
        proxy=True


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    sub_category = models.ForeignKey(
        SubCategory,on_delete=models.CASCADE,default='')
    description = models.CharField(max_length=200, default='',null=True , blank=True)
    image = models.ImageField(upload_to='uploads/products/',default='',null=True )


    def __str__(self):
        return self.name

    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in =ids)

class Customer(models.Model):
    name =models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=500)

    def register(self):
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except:
            return False


    def doExists(self):
        if Customer.objects.filter(email=self.email):
            return True

        return False

    def validateEmail(self):
        email=self.email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False


    def validatePhone(self):
            phone = self.phone
            from django.core.exceptions import ValidationError
            try:
                int(phone)
                return True
            except (ValueError, TypeError,ValidationError):
                return False



class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, default='', blank=True)
    phone = models.CharField(max_length=50, default='', blank=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def placeOrder(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')

