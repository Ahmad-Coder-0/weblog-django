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
    post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED)
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
            print('redirecting')
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
            results = (results1 | results2).order_by('-similarity')
    context = {
        'query': query,
        'results': results,
    }
    print(results)
    return render(request, 'blog/pages/search.html', context)
