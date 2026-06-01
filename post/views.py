from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, DeleteView, CreateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


def index(request):
    return render(request, 'blog/pages/index.html')


class PostListView(ListView):
    queryset = Post.published.all().order_by('-publish')
    paginate_by = 2
    template_name = 'blog/pages/post_list.html'
    context_object_name = 'posts'

# def post_list(request):
#     posts = Post.published.order_by('-publish')
#     paginator = Paginator(posts, 2)
#     page_number = request.GET.get('page', 1)
#     posts = paginator.get_page(page_number)
#     context = {
#         'posts': posts,
#     }
#     return render(request, 'blog/pages/post_list.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/pages/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        user = self.request.user
        if post.status != "PB" and user != post.author:
            raise PermissionDenied

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.object

        context['comments'] = post.comments.filter(active=True)
        context['form'] = CommentForm()
        return context

# def post_detail(request, pk):
#     user = request.user
#     post = get_object_or_404(Post, id=pk)
#     if post.status != "PB" and user != post.author:
#         raise PermissionDenied
#     comments = post.comments.filter(active=True)
#     form = CommentForm()
#     context = {
#         'post': post,
#         'form': form,
#         'comments': comments,
#     }

#     return render(request, 'blog/pages/post_detail.html', context)


class TicketCreateView(LoginRequiredMixin, FormView):
    model = Ticket
    template_name = 'blog/forms/ticket.html'
    form_class = TicketForm
    success_url = reverse_lazy('post:index')

    def form_valid(self, form):
        data = form.cleaned_data

        Ticket.objects.create(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            title=data['title'],
            description=data['description'],
            subject=data['subject'],
        )

        return super().form_valid(form)

# @login_required
# def tickets(request):
#     if request.method == 'POST':
#         form = TicketForm(request.POST)
#         if form.is_valid():
#             Ticket.objects.create(
#                 name=form.cleaned_data['name'],
#                 email=form.cleaned_data['email'],
#                 phone=form.cleaned_data['phone'],
#                 title=form.cleaned_data['title'],
#                 description=form.cleaned_data['description'],
#                 subject=form.cleaned_data['subject'],
#             )
#             return redirect('post:index')
#     else:
#         form = TicketForm()
#     context = {
#         'form': form,
#     }
#     return render(request, 'blog/forms/ticket.html', context)


class PostCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']
    template_name = 'blog/forms/comment.html'

    def post(self, request, pk, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post, id=pk, status=Post.Status.PUBLISHED)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.post = self.post_obj
        comment = form.save()

        context = {
            'form': form,
            'post': self.post_obj,
            'comment': comment
        }
        return self.render_to_response(context)

# @require_POST
# def post_comment(request, pk):
#     post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
#     comment = None
#     form = CommentForm(data=request.POST)
#     if form.is_valid():
#         comment = form.save(commit=False)
#         comment.post = post
#         comment.save()

#     context = {
#         'form': form,
#         'post': post,
#         'comment': comment,
#     }
#     return render(request, 'blog/forms/commnet.html', context)


class SearchView(View):
    def get(self, request, *args, **kwargs):
        query = None
        results = []
        if 'query' in request.GET:
            form = SearchForm(data=request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']
                # ۱. جستجو در عنوان و توضیحات خود پست
                results1 = Post.published.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gt=0.1)
                results2 = Post.published.annotate(
                    similarity=TrigramSimilarity('description', query)
                ).filter(similarity__gt=0.17)
                results3 = Post.published.annotate(
                    similarity=TrigramSimilarity('images__title', query)
                ).filter(similarity__gt=0.1)
                results4 = Post.published.annotate(
                    similarity=TrigramSimilarity('images__description', query)
                ).filter(similarity__gt=0.1)
                results = (results1 | results2 | results3 |
                           results4).distinct().order_by('-similarity')
        context = {
            'query': query,
            'results': results,
        }
        return render(request, 'blog/pages/search.html', context)


class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'blog/pages/profile.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return self.request.user.posts.all().order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

# @login_required
# def profile(request):
#     user = request.user
#     posts = user.posts.all().order_by('-created')

#     context = {
#         'user': user,
#         'posts': posts,
#     }
#     return render(request, 'blog/pages/profile.html', context)


@login_required
def add_post(request):
    if request.method == "POST":
        form = AddPostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            formset.instance = post
            formset.save()

            return redirect("post:profile")
    else:
        form = AddPostForm()
        formset = ImageFormSet()

        context = {
            'form': form,
            'formset': formset,
        }
    return render(request, "blog/forms/add_post.html", context)


@login_required
def delete_post(request, pk):
    user = request.user
    post = get_object_or_404(Post, id=pk)
    if not user == post.author:
        raise PermissionDenied
    if request.method == "POST":
        confirm = request.POST.get('delete')
        if confirm == "DEL":
            post.delete()
        return redirect("post:profile")

    return render(request, "blog/forms/delete_post.html", {'post': post})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == "POST":
        form = AddPostForm(request.POST, instance=post)
        formset = ImageFormSet(request.POST, request.FILES, instance=post)
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.status = Post.Status.DRAFT
            post.save()
            formset.save()

            return redirect('post:profile')
    form = AddPostForm(instance=post)
    formset = ImageFormSet(instance=post)
    context = {
        'form': form,
        'formset': formset,
        'post': post,
    }
    return render(request, 'blog/forms/edit_post.html', context)


# def user_login(request):
#     if not request.user.is_authenticated:
#         if request.method == "POST":
#             form = LoginForm(request.POST)
#             if form.is_valid():
#                 cd = form.cleaned_data
#                 user = authenticate(
#                     request, username=cd['username'], password=cd['password'])
#                 if user is not None:
#                     if user.is_active:
#                         login(user)
#                         return redirect("post:profile")
#                     else:
#                         return HttpResponse("حساب شما غیر فعال است لطفا با پشتیبانی تماس بگیرید")
#                 else:
#                     return HttpResponse("نام کاربری یا رمز عبور شما اشتباه است")
#         else:
#             form = LoginForm()
#         context = {
#             'form': form,
#         }
#         return render(request, 'registration/login.html', context)
#     else:
#         return redirect("post:profile")


def register(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = form.save(commit=False)
                user.set_password(cd['password'])
                user.save()
                Account.objects.create(user=user)
                login(request, user)
                return redirect("post:profile")
        else:
            form = UserRegisterForm()
        context = {
            'form': form,
        }
        return render(request, 'registration/register.html', context)
    else:
        return redirect("post:profile")


@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=user)
        account_form = EditAccountForm(
            request.POST, request.FILES, instance=user.account)
        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
            return redirect("post:profile")
    else:
        user_form = EditUserForm(instance=user)
        account_form = EditAccountForm(instance=user.account)

    context = {
        'user_form': user_form,
        'account_form': account_form,
    }
    return render(request, 'registration/edit-user-profile.html', context)
