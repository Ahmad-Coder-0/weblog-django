from ast import Add

from bson import is_valid
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity


def index(request):
    return render(request, 'blog/pages/index.html')


def post_list(request):
    posts = Post.published.order_by('-publish')
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    context = {
        'posts': posts,
    }
    return render(request, 'blog/pages/post_list.html', context)


def post_detail(request, pk):
    user = request.user
    post = get_object_or_404(Post, id=pk)
    if not user == post.author:
        post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'blog/pages/post_detail.html', context)


def tickets(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            Ticket.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                subject=form.cleaned_data['subject'],
            )
            return redirect('post:index')
    else:
        form = TicketForm()
    context = {
        'form': form,
    }
    return render(request, 'blog/forms/ticket.html', context)


@require_POST
def post_comment(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    context = {
        'form': form,
        'post': post,
        'comment': comment,
    }
    return render(request, 'blog/forms/commnet.html', context)


def search_post(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results1 = Post.published.annotate(
                similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1)
            results2 = Post.published.annotate(
                similarity=TrigramSimilarity('description', query)).filter(similarity__gt=0.17)
            results3 = Post.images.annotate(
                similarity=TrigramSimilarity('title', query))
            results4 = Post.images.annotate(
                similarity=TrigramSimilarity('description', query))

            results = (results1 | results2 | results3 |
                       results4).order_by('-similarity')
    context = {
        'query': query,
        'results': results,
    }
    print(results)
    return render(request, 'blog/pages/search.html', context)


def profile(request):
    user = request.user
    posts = user.posts.all().order_by('-created')

    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'blog/pages/profile.html', context)


def add_post(request):
    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if form.cleaned_data.get('image_1'):
                Image.objects.create(
                    image_file=form.cleaned_data['image_1'],
                    post=post,
                    title=form.cleaned_data['image_1_title'],
                    description=form.cleaned_data['image_1_description'])
            if form.cleaned_data.get('image_2'):
                Image.objects.create(
                    image_file=form.cleaned_data['image_2'],
                    post=post,
                    title=form.cleaned_data['image_2_title'],
                    description=form.cleaned_data['image_2_description'])

            return redirect("post:profile")
    else:
        form = AddPostForm()

        context = {
            'form': form
        }
    return render(request, "blog/forms/add_post.html", context)
