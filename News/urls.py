from django.urls import path
from .views import (
    PostsList, PostDetail, PostSearch, PostCreate, PostUpdate, PostDelete, CategoryList, subscribe
)

urlpatterns = [
    path('', PostsList.as_view(), name='post_list'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('categories/<int:pk>', CategoryList.as_view(), name='category_list'),
    path('categories/<int:pk>/subscribe', subscribe, name='subscribe')
]