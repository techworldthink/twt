from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count
from .models import Category, Product, OrderItem, Order, Supplier, Purchase, PurchaseItem
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, ProductForm, CategoryForm, SupplierForm, PurchaseForm, PurchaseItemFormSet
import urllib.parse

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    query = request.GET.get('query')
    if query:
        products = products.filter(name__icontains=query)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
        'cart_product_form': CartAddProductForm()
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    return render(request, 'shop/product/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form
    })

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
    return redirect('shop:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('shop:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'shop/cart/detail.html', {'cart': cart})

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in cart:
                # Get the latest cost price for this product
                latest_purchase_item = PurchaseItem.objects.filter(product=item['product']).order_by('-purchase__date').first()
                cost_price = latest_purchase_item.cost_price if latest_purchase_item else item['product'].price * 0.7 # fallback 
                
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    cost_price=cost_price,
                    quantity=item['quantity']
                )
                # Deduct stock
                product = item['product']
                product.stock -= item['quantity']
                product.save()
            # Clear the cart
            cart.clear()
            
            # Generate WhatsApp message
            message = f"Hello, I would like to confirm my order #{order.id}.\n\nItems:\n"
            for item in order.items.all():
                message += f"- {item.product.name} x {item.quantity} (${item.get_cost()})\n"
            message += f"\nTotal: ${order.get_total_cost()}\n"
            message += f"\nDetails:\nName: {order.full_name}\nPhone: {order.phone}\nAddress: {order.address}, {order.city}"
            
            whatsapp_url = f"https://wa.me/919999999999?text={urllib.parse.quote(message)}" # Placeholder number
            
            return render(request, 'shop/order/created.html', {
                'order': order,
                'whatsapp_url': whatsapp_url
            })
    else:
        form = OrderCreateForm()
    return render(request, 'shop/order/create.html', {
        'cart': cart,
        'form': form
    })

# Admin Dashboard Views
def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_dashboard(request):
    paid_orders = Order.objects.filter(paid=True)
    turnover = paid_orders.aggregate(Sum('items__price'))['items__price__sum'] or 0
    total_cost = paid_orders.aggregate(Sum('items__cost_price'))['items__cost_price__sum'] or 0
    profit = turnover - total_cost
    
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    recent_orders = Order.objects.all().order_by('-created')[:5]
    
    # Low stock alerts
    low_stock_products = Product.objects.filter(stock__lt=5, available=True)
    
    return render(request, 'shop/dashboard/index.html', {
        'turnover': turnover,
        'profit': profit,
        'total_orders': total_orders,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products
    })

@user_passes_test(is_staff)
def admin_products(request):
    products = Product.objects.all()
    query = request.GET.get('query')
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'shop/dashboard/products.html', {'products': products, 'query': query})

@user_passes_test(is_staff)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created')
    return render(request, 'shop/dashboard/orders.html', {'orders': orders})

@user_passes_test(is_staff)
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_products')
    else:
        form = ProductForm()
    return render(request, 'shop/dashboard/product_form.html', {'form': form, 'action': 'Add'})

@user_passes_test(is_staff)
def admin_product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/dashboard/product_form.html', {'form': form, 'action': 'Edit', 'product': product})

@user_passes_test(is_staff)
def admin_product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        return redirect('shop:admin_products')
    return render(request, 'shop/dashboard/product_confirm_delete.html', {'product': product})

@user_passes_test(is_staff)
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'shop/dashboard/categories.html', {'categories': categories})

@user_passes_test(is_staff)
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'shop/dashboard/category_form.html', {'form': form, 'action': 'Add'})

@user_passes_test(is_staff)
def admin_category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'shop/dashboard/category_form.html', {'form': form, 'action': 'Edit', 'category': category})

@user_passes_test(is_staff)
def admin_category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        return redirect('shop:admin_categories')
    return render(request, 'shop/dashboard/category_confirm_delete.html', {'category': category})

@user_passes_test(is_staff)
def admin_order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'shop/dashboard/order_detail.html', {'order': order})

@user_passes_test(is_staff)
def admin_order_toggle_paid(request, id):
    order = get_object_or_404(Order, id=id)
    order.paid = not order.paid
    order.save()
    return redirect('shop:admin_order_detail', id=order.id)

@user_passes_test(is_staff)
def admin_order_update_status(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
    return redirect('shop:admin_order_detail', id=order.id)

@user_passes_test(is_staff)
def admin_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'shop/dashboard/suppliers.html', {'suppliers': suppliers})

@user_passes_test(is_staff)
def admin_supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_suppliers')
    else:
        form = SupplierForm()
    return render(request, 'shop/dashboard/supplier_form.html', {'form': form, 'action': 'Add'})

@user_passes_test(is_staff)
def admin_purchases(request):
    purchases = Purchase.objects.all()
    return render(request, 'shop/dashboard/purchases.html', {'purchases': purchases})

@user_passes_test(is_staff)
def admin_purchase_create(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            purchase = form.save()
            formset.instance = purchase
            formset.save()
            return redirect('shop:admin_purchases')
    else:
        form = PurchaseForm()
        formset = PurchaseItemFormSet()
    return render(request, 'shop/dashboard/purchase_form.html', {
        'form': form,
        'formset': formset,
        'action': 'Add'
    })

@user_passes_test(is_staff)
def admin_reports(request):
    # Turnover (Total Sales of paid orders)
    paid_orders = Order.objects.filter(paid=True)
    turnover = paid_orders.aggregate(Sum('items__price'))['items__price__sum'] or 0
    
    # Total Cost of items in paid orders
    total_cost = paid_orders.aggregate(Sum('items__cost_price'))['items__cost_price__sum'] or 0
    
    profit = turnover - total_cost
    margin = (profit / turnover * 100) if turnover > 0 else 0
    
    return render(request, 'shop/dashboard/reports.html', {
        'turnover': turnover,
        'total_cost': total_cost,
        'profit': profit,
        'margin': margin,
        'total_orders': paid_orders.count()
    })
