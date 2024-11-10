from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

from .models import Product, Category, ReviewRating, ProductGallery
from .forms import ReviewForm
from cart.views import _cart_id
from cart.models import CartItem
from orders.models import OrderProduct

def home(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'shop/index.html', {'products': products})

def shop(request, category_slug=None):
    categories = None
    products = Product.objects.filter(is_available=True)
    
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=categories)

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    products_count = products.count()

    context = {
        'category_slug': category_slug,
        'products': paged_products,
        'products_count': products_count,
    }
    return render(request, 'shop/shop/shop.html', context)

def product_details(request, category_slug, product_details_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_details_slug)
    except Product.DoesNotExist:
        return redirect('shop:home')

    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists() if request.user.is_authenticated else None
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True).order_by('-updated_at')
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'shop/shop/product_details.html', context)

def search(request):
    products = Product.objects.none()
    products_count = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            products_count = products.count()
    
    context = {
        'products': products,
        'products_count': products_count,
    }
    return render(request, 'shop/shop/search.html', context)

def review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user_id=request.user.id, product_id=product_id)
            form = ReviewForm(request.POST, instance=review)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
        
        if form.is_valid():
            data = form.save(commit=False)
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = product_id
            data.user_id = request.user.id
            data.save()
            messages.success(request, 'Thank you, your review has been posted!')
        else:
            messages.error(request, 'An error occurred while submitting your review.')
        
        return redirect(url)
