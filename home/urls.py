


from django.urls import path,include
from . import views
from .views import Login,Register,Index,Cart,CheckOut,Search,OrderView,Detail,Account, About, Contact, Coupons,Wishlist,Service
from .views import logout
from .middlewares.auth import auth_middleware


urlpatterns = [
    path('', Index.as_view(),name='index_all'),
    path('<str:parent_or_child>/<int:pk>',Index.as_view(),name='index'),
    path('login',Login.as_view(),name='login'),
    path('register',Register.as_view(),name='register'),
    path('logout',logout,name='logout'),
    path('cart',auth_middleware(Cart.as_view()),name='cart'),
    path('wishlist', Wishlist.as_view(),name='wishlist'),
    path('about', About.as_view(),name='about'),
    path('contact', Contact.as_view(), name='contact'),
    path('account', Account.as_view(), name='account'),
    path('service', Service.as_view(), name='service'),
    path('coupons', Coupons.as_view(), name='coupons'),
    path('check-out',CheckOut.as_view(),name='checkout'),
    path('search',Search.as_view(),name='search'),
    path('orders',auth_middleware(OrderView.as_view()), name='orders'),
    path('product_detail/<slug:slug>/',Detail.as_view(),name='detail'),
]
