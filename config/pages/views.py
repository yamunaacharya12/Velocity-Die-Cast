from django.shortcuts import render, get_object_or_404
from .models import BlogPost


def faq(request):
    faqs = [
        ('What scales do you carry?',
         'We carry 1:64 (pocket scale), 1:43 (display scale), and 1:18 (museum scale) models across all brands.'),
        ('Are these real metal die-cast?',
         'Yes — every model uses a zinc-alloy die-cast body. Only select interior and chassis trim pieces use ABS plastic.'),
        ('Do you ship to Nepal and South Asia?',
         'Yes, we ship worldwide including Nepal, India, Bangladesh, and Sri Lanka, typically arriving in 7–10 business days.'),
        ('Can I cancel my order after placing it?',
         'Orders can be cancelled within 2 hours of placement from My Account → Order History, before they enter packing.'),
        ('Do limited-edition models restock?',
         'No — limited and numbered editions are one-time production runs and do not restock once sold out.'),
        ('What payment methods do you accept?',
         'Credit/debit card, PayPal, eSewa, Khalti, Fonepay, and Cash on Delivery.'),
    ]
    return render(request, 'website/faq.html', {'faqs': faqs})


def shipping_info(request):
    return render(request, 'website/shipping.html')


def returns_policy(request):
    return render(request, 'website/returns.html')


def privacy_policy(request):
    return render(request, 'website/privacy.html')


def terms(request):
    return render(request, 'website/terms.html')


def blog_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'website/blog.html', {'posts': posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'website/blog_detail.html', {'post': post})
