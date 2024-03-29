from django.urls import path

from . import views

urlpatterns = [
    path("listings", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories", views.categories, name="categories"),
    path("category/<str:categ_name>", views.category, name="category"),
    path("user/<str:username>", views.user, name="user"),
    path("listings/<int:listing_id>", views.listing, name="listing")
]
