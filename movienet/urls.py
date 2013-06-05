__author__ = 'ytang'

from django.conf.urls import patterns, url
from movienet import views

urlpatterns = patterns('',

    url(r'^login/$', views.login,name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^(?P<user_id>\d+)/$',views.home,name = 'home'),
    url(r'^search_people/$',views.search_people,name = 'search_people'),
    url(r'^u/(?P<user_id>\d+)/$', views.visit_other_user_home_page,name ='visit' ),
    url(r'^handle_request/$', views.handle_friend_request, name='request_handler'),
    url(r'^send_message/(?P<friend_id>\d+)/$', views.send_message, name='send_massage'),
    url(r'^status/$',views.status,name="send_status"),
    url(r'^search_movie/$', views.search_movie, name='search_movie'),
    url(r'^movie/(?P<movie_id>\d+)/$',views.get_movie, name='get_movie'),
    url(r'^movie/(?P<movie_id>\d+)/rate/$', views.rate_movie, name='rate_movie'),
    url(r'^r/(?P<review_id>\d+)', views.comment, name='get_comment'),
    url(r'^r/comment/(?P<review_id>\d+)/(?P<to_user_id>\d+)/$',views.make_comment, name='make_comment'),
    url(r'^r/comment/(?P<review_id>\d+)/(?P<to_user_id>\d+)/submit/$',views.submit_comment, name='submit_comment'),
    url(r'^performer/movie/(?P<performer_id>\d+)/$', views.show_movies_of_actors, name='show_all_movies'),
    url(r'^director/movie/(?P<director_id>\d+)/$', views.show_movies_of_directors, name='show_all_movies_director'),
    url(r'^recommend_movie/$', views.recommend_movie_for_user, name='recommend_movie'),
    url(r'^friend_request/$', views.send_friend_request, name = 'send_friend_request')


)
