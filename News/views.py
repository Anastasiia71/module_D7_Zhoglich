from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from .filters import PostFilter
from .forms import PostForm
from .models import Post, Category
from .tasks import notify_about_new_post, notify_weekly


class WeekView(View):
    def get(self, request):
        notify_about_new_post.delay()
        return redirect("/")


class WeeklyView(View):
    def get(self, request):
        notify_weekly.delay()
        return redirect("/")


class PostsList(ListView):
    model = Post
    ordering = 'dateCreation'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10


class PostDetail(DetailView):
    model = Post
    template_name = 'id_news.html'
    context_object_name = 'id_news'


class PostSearch(ListView):
    model = Post
    ordering = 'title'
    template_name = 'news_search.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('News.add_post')
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('News.change_post')
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'


class PostDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('post_list')


class CategoryList(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(postCategory=self.category).order_by('dateCreation')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['postCategory'] = self.category
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = 'Вы успешно подписались на рассылку новостей категории'
    return render(request, 'subscribe.html', {'category':category, 'message':message})
