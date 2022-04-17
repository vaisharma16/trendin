from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect,HttpResponseRedirect
from .models import Category,SubCategory,Product,Customer,Order
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.views import View
from django.db.models import Q
from home.middlewares.auth import auth_middleware
from django.utils.decorators import method_decorator

class Index(View):
    def post(self, request):
        product=request.POST.get('product')
        remove=request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        #print('cart' ,request.session['cart'])
        return redirect('index_all')

    def get(self,request,parent_or_child=None,pk=None):
        cart = request.session.get('cart')
        #email=request.session.get('email')
        if not cart:
            request.session['cart'] = {}
        categories=Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'subcategory':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'category':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products=[]
        #print('you are : ', request.session.get('email'))
        #print(email)
        return render(
            request,
            'products/index.html',
            {'categories':categories,'products':products}
            )


class Register(View):
    def get(self,request):
        return render(request, 'products/register.html')

    def post(self,request):
        postData = request.POST
        name = postData.get('name')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        # validation
        value = {'name': name, 'phone': phone, 'email': email}
        customer = Customer(name=name, phone=phone, email=email, password=password)
        err_msg = self.validateCustomer(customer)

        # saving
        if not err_msg:
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('login')
        else:
            data = {'error': err_msg, 'values': value}
            return render(request, "products/register.html", data)

    def validateCustomer(self,customer):
        err_msg = None
        if (not customer.name):
            err_msg = "Name Required!"
        elif (not customer.phone):
            err_msg = "Phone No. required"
        elif not customer.validatePhone():
            err_msg = "Enter valid Phone no."
        elif len(customer.phone) < 10:
            err_msg = "Phone No. must have 10 digits"
        elif not customer.validateEmail():
            err_msg = 'Enter valid email'
        elif not customer.password:
            err_msg = "please create a password"
        elif len(customer.password) < 6:
            err_msg = "Password must be 6 char long"
        elif customer.doExists():
            err_msg = 'Email Address Already registered..'
        return err_msg


class Login(View):
    def get(self, request, parent_or_child=None,pk=None):
        Login.return_url = request.GET.get('return_url')
        categories=Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'child':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'parent':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products=[]
        return render(request, 'products/login.html',{'categories':categories,'products':products}
            )

    def post(self, request):

        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        err_msg = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id
                request.session['email'] = customer.email
                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('index_all')
            else:
                err_msg = 'Email or Password invalid'
        else:
            err_msg = 'Email or Password invalid'
        return render(request, 'products/login.html', {'error': err_msg})




def logout(request):
    request.session.clear()
    return redirect('/login')


class Cart(View):
    def get(self, request,parent_or_child=None,pk=None):

        ids=list(request.session.get('cart').keys())
        productss=Product.get_products_by_id(ids)
        categories = Category.objects.filter(parent=None)
        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'subcategory':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'category':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products=[]

        return render(request, 'products/cart.html',{'products': products,'productss':productss,'categories':categories})

class CheckOut(View):
    def post(self , request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))
        print(address, phone, customer, cart, products)

        for product in products:
            print(cart.get(str(product.id)))
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart'] = {}

        return redirect('cart')


class Search(View):

    def post(self, request):
        product=request.POST.get('product')
        remove=request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        return render(request, 'products/search.html',cart)

    def get(self,request):
        kw = self.request.GET.get('search')
        products = Product.objects.filter(Q(name__icontains=kw) | Q(description__icontains=kw))
        context={}
        context['products'] = products
        context['kw'] = kw
        return render(request, 'products/search.html',context)


class OrderView(View):

    def post(self, request):
        product=request.POST.get('product')
        remove=request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        return redirect('orders')

    def get(self , request ):

        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        return render(request , 'products/orders.html'  , {'orders' : orders})        

class Detail(View):
    def get(self,request,slug):
        product=Product.objects.get(slug=slug)
        context={}
        context['product']=product
        return render(request,'products/product_detail.html',context)

class About(View):
    def get(self,request, parent_or_child=None,pk=None):
        categories = Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'child':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'parent':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products = []
        return render(request, 'products/about.html', {'categories': categories, 'products': products}
                      )

class Wishlist(View):
    def get(self,request, parent_or_child=None,pk=None):
        categories = Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'child':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'parent':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products = []
        return render(request, 'products/wishlist.html', {'categories': categories, 'products': products}
                      )

class Account(View):
    def get(self,request, parent_or_child=None,pk=None):
        categories = Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'child':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'parent':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products = []
        return render(request, 'products/my-account.html', {'categories': categories, 'products': products}
                      )

class Contact(View):
    def get(self,request, parent_or_child=None,pk=None):
        categories = Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'child':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'parent':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products = []
        return render(request, 'products/contact-us.html', {'categories': categories, 'products': products}
                      )

class Service(View):
    def get(self,request, parent_or_child=None,pk=None):
        categories = Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'child':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'parent':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products = []
        return render(request, 'products/service.html', {'categories': categories, 'products': products}
                      )

class Coupons(View):
    def get(self,request, parent_or_child=None,pk=None):
        categories = Category.objects.filter(parent=None)

        if parent_or_child is None:
            products = Product.objects.all()
        elif parent_or_child == 'child':
            sub_cat = SubCategory.objects.get(pk=pk)
            products = sub_cat.product_set.all()

        elif parent_or_child == 'parent':
            products = []
            sub_cats = Category.objects.get(pk=pk).children.all()

            for sub_cat in sub_cats:
                prds = sub_cat.product_set.all()
                products += prds

        else:
            products = []
        return render(request, 'products/coupons.html', {'categories': categories, 'products': products}
                      )