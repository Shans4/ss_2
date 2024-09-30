from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('categories/<int:category_id>/', views.category_articles, name='category_articles'),
    path('articles/<int:article_id>/', views.article_detal, name='article_detal'),

    path('account/', views.account_view, name='account'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('articles/create/', views.create_article_view, name='create'),
    path('articles/<int:pk>/update/', views.UpdateArticleView.as_view(), name='update'),
    path('articles/<int:pk>/delete/', views.DeleteArticleView.as_view(), name='delete'),

    path('<str:obj_type>/<int:obj_id>/<str:action>/', views.add_vote, name='add_vote'),

    path('search/',views.search_view, name='search_view'),

    path('article/<int:article_id>/add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('article/<int:article_id>/remove_from_favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.favorites_list, name='favorites_list')
]
