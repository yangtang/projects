# Create your views here.
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import ensure_csrf_cookie
from form import RegisterForm, LogInForm
from models import *
from django.template import RequestContext
from django.http import  HttpResponseRedirect
from django.contrib.auth.models import User
from itertools import chain
from django.db.models import Count
from django.db.models import Avg
import re
@ensure_csrf_cookie
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            info = form.cleaned_data

            User.objects.create_user(info['email'],email=info['email'],password=info['password'])

            UserProfile.objects.create(first_name = info['first_name'], last_name = info['last_name'],
            birthday = info['birthday'], gender = info['gender'], email = info['email'], create_time=datetime.now() )
            return HttpResponseRedirect(reverse('login'))
    else:
         form =RegisterForm()
    return render_to_response('register.html',{'form':form},RequestContext(request))

@ensure_csrf_cookie
def login(request):
    errors = []
    if request.method =='POST':
      form = LogInForm(request.POST)
      if form.is_valid():
          info  = form.cleaned_data
          username = info['email']
          password = info['password']
          user = authenticate(username = username, password = password)
          if user is not None:
              if user.is_active:
                  auth_login(request, user)
                  username = user.username
                  user_id = UserProfile.objects.get(email=username).id
                  return HttpResponseRedirect(reverse('home',kwargs={'user_id':user_id} ))
              else:
                  errors.append('The user account is disabled')
          else:
             errors.append('Invalid username or password')
    else:
        form = LogInForm()
    return render_to_response('login.html',{'form': form, 'errors': errors}, RequestContext(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('login'))

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/movienet/login/')
def home(request, user_id):
    if request.user.username != UserProfile.objects.get(id=user_id).email:
        return HttpResponseRedirect(reverse('login'))

    name=UserProfile.objects.get(id= user_id)

    friend_request=Request.objects.filter(to_who=user_id)

    friend_list=Friendship.objects.filter(friend_one=user_id)

    friend_list_id=[]

    friend_list_id.append(user_id)
    for f in friend_list:
        friend_list_id.append(f.friend_two.id)

    message_from = Message.objects.filter(from_who=user_id)
    message_to=Message.objects.filter(to_who=user_id)
    message=list(chain(message_from,message_to))
    message.sort(key=lambda mes:mes.time, reverse=True)

    status=Status.objects.filter(user=user_id)

    feed = User_rating_and_review.objects.filter(user__in=friend_list_id).order_by('-time')

    feeds=[]
    for f in feed:
        movie_id= f.movie.mid
        poster=Movie_poster.objects.filter(movie=movie_id)
        if poster:
          d=dict(text=f,image=poster[0])
          feeds.append(d)

    reply = Comment_to_rating_and_review.objects.filter(to_who=user_id).order_by('-time')


    return render_to_response('homepage.html',{'user': name, 'friend_request':friend_request, 'friend_list':friend_list,
                                          'message':message,'status':status,'feed':feeds,'reply':reply},RequestContext(request))

def search_people(request):
    user_id = UserProfile.objects.get(email=request.user.username)
    error = False
    result_list=[]
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            name = q.split(' ')
            for n in name:
                namelist1 = UserProfile.objects.filter(first_name__icontains=n)
                namelist2 = UserProfile.objects.filter(last_name__icontains=n)
                result_list = list(chain(result_list,namelist1,namelist2))
            result_list= list(set(result_list))
            return render_to_response('search_people.html', {'user':user_id,'results':result_list,'query':q},RequestContext(request))
    return HttpResponseRedirect(reverse('home',kwargs={'user_id':user_id.id}))

@ensure_csrf_cookie
def send_friend_request(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('id',''):
            errors.append('Select a person you want to be friend with')
        if not errors:
            user_id=UserProfile.objects.get(email=request.user)
            friend_id=UserProfile.objects.get(pk=request.POST['id'])
            request_message =request.POST.get('message')
            request_time = datetime.now()
            Request.objects.create(from_who = user_id, to_who=friend_id, message=request_message,time = request_time)
            return HttpResponseRedirect(reverse('home',kwargs={'user_id':user_id.id}))
    return render_to_response('search_people.html',{'errors':errors},RequestContext(request))

def visit_other_user_home_page(request, user_id):
    username = UserProfile.objects.get(id=user_id)
    myself= UserProfile.objects.get(email=request.user.username)
    message_from = Message.objects.filter(from_who=username.id, to_who=myself.id)
    message_to=Message.objects.filter(from_who=myself.id, to_who=username.id)
    message=list(chain(message_from,message_to))
    message.sort(key=lambda mes:mes.time, reverse=True)

    feed = User_rating_and_review.objects.filter(user=user_id).order_by('-time')

    feeds=[]
    for f in feed:
        movie_id= f.movie.mid
        poster=Movie_poster.objects.get(movie=movie_id)
        d=dict(text=f,image=poster)
        feeds.append(d)
    return render_to_response('guestpage.html',{'owner':username,'user':myself,'message':message,'feed':feeds}, RequestContext(request))


def handle_friend_request(request):
    user_id=UserProfile.objects.get(email=request.user.username)
    if request.method =='POST':
        if request.POST.get('choice',''):
            choice=request.POST['choice'].split(' ')
            request_id = choice[0]
            decision= choice[1]
            req=Request.objects.get(id=request_id)
            if decision=='y':
                b1=Friendship(friend_one=req.from_who, friend_two=req.to_who, time=datetime.now())
                b1.save()
                b2=Friendship(friend_one=req.to_who, friend_two=req.from_who, time=datetime.now())
                b2.save()
            req.delete()
    return HttpResponseRedirect(reverse('home',kwargs={'user_id':user_id.id}))

def send_message(request, friend_id):
    user_id=UserProfile.objects.get(email=request.user.username).id
    if request.method =='POST':
        if request.POST.get('message',''):
            message = request.POST['message']
            friend = UserProfile.objects.get(id=friend_id)
            user = UserProfile.objects.get(id=user_id)
            Message.objects.create(from_who=user, to_who=friend, content=message,  time=datetime.now())
    return HttpResponseRedirect(reverse('visit', kwargs={'user_id':friend_id}))


def status(request):
    user_id=UserProfile.objects.get(email=request.user.username)
    if request.method =='POST':
        if request.POST.get('status',''):
            new_status=request.POST['status']
            Status.objects.create(user= user_id, content=new_status, time=datetime.now())
    return HttpResponseRedirect(reverse('home',kwargs={'user_id':user_id.id}))


def search_movie(request):
    user_id = UserProfile.objects.get(email=request.user.username)
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            movies=Movie_rating.objects.filter(movie__title__icontains=q).order_by('-vote')
            highly_possible_movie=[]
            pat= re.compile(r""".*? \(\d+\)(?! \(.*?\))""")
            for m in movies:
                if  pat.match(m.movie.title) :
                    highly_possible_movie.append(m)
            results=[]
            for m in highly_possible_movie:
                poster=Movie_poster.objects.filter(movie=m.movie)
                temp= dict([('movie',m),('poster',poster)])
                results.append(temp)
            return render_to_response('search_movie.html',{'user':user_id,'movies':results},RequestContext(request))
    return HttpResponseRedirect(request.path)

def get_movie(request, movie_id):
    user_id = UserProfile.objects.get(email=request.user.username)

    movie=Movie.objects.get(mid=movie_id)

    average_rating=User_rating_and_review.objects.filter(movie=movie_id).aggregate(Avg('rating'))

    mapp=Movie_certificate.objects.filter(movie=movie_id,country='USA')

    rating=Movie_rating.objects.filter(movie=movie_id)

    poster=Movie_poster.objects.filter(movie=movie_id)

    genre=Movie_genre.objects.filter(movie=movie_id)

    runtime=Movie_runtime.objects.filter(movie=movie_id)

    director=Movie_director.objects.filter(movie=movie_id)

    star=Movie_role.objects.filter(movie=movie_id).annotate(null_credit=Count('credit')).order_by('-null_credit','credit')[0:6]

    user_rating=User_rating_and_review.objects.filter(movie=movie_id, user=user_id.id)

    critic_review=Movie_review.objects.filter(movie=movie_id)
    positive=[]
    negative=[]
    if critic_review:
       for c in critic_review:
          if c.freshness == 'fresh':
              positive.append(c)
          else:
              negative.append(c)

    recommend_movie=Content_base_recommend_movie.objects.filter(movie=movie_id).order_by('id')[:10]

    recommend_movie_list=[]
    for r in recommend_movie:
        movie_with_poster = Movie_poster.objects.filter(movie=r.recommend_movie.mid)
        if movie_with_poster:
           recommend_movie_list.append(movie_with_poster)
    return render_to_response('movie.html',{'user':user_id,'movie':movie,'mapp':mapp,'rating':rating,'poster':poster,'genre':genre,
                                           'runtime':runtime,'director':director,'star':star,'user_rating':user_rating,'average_rating':average_rating,
                                           'positive_critic':positive,'negative_critic':negative,'recommend_movie':recommend_movie_list},RequestContext(request)
                         )



def rate_movie(request, movie_id):
    user_id=UserProfile.objects.get(email=request.user.username)
    if request.method =='POST':
        if request.POST.get('choice',''):
            rate=request.POST['choice']
            rated_movie=Movie.objects.get(mid=movie_id)
            r=User_rating_and_review.objects.create(movie=rated_movie,user=user_id,rating=rate,time=datetime.now())
            if request.POST.get('review',''):
               r.review=request.POST['review']
               r.save()
    return HttpResponseRedirect(reverse('get_movie',kwargs={'movie_id':movie_id}))


def comment(request, review_id):
    user_id=UserProfile.objects.get(email=request.user.username)
    review=User_rating_and_review.objects.get(pk=review_id)
    comments=Comment_to_rating_and_review.objects.filter(review=review_id).order_by('-time')
    return render_to_response('review_comment.html',{'review':review,'comments':comments,'user':user_id},RequestContext(request))


def make_comment(request, review_id, to_user_id):
    return render_to_response('commentpage.html',{'review':review_id,'to_user':to_user_id},RequestContext(request))

def submit_comment(request,review_id, to_user_id):
    user_id=UserProfile.objects.get(email=request.user.username)
    if request.method == 'POST':
        if request.POST.get('comment',''):
            one_comment=request.POST['comment']
            one_review=User_rating_and_review.objects.get(pk=review_id)
            one_user=UserProfile.objects.get(pk=to_user_id)
            Comment_to_rating_and_review.objects.create(review=one_review,from_who=user_id,to_who=one_user,comment=one_comment,time=datetime.now())
    return HttpResponseRedirect(reverse('get_comment', kwargs={'review_id':review_id}))


def show_movies_of_actors(request, performer_id):
     user_id=UserProfile.objects.get(email=request.user.username)
     movies=Movie_poster.objects.filter(movie__movie_role__performer=performer_id)
     performer=Performer.objects.get(pk=performer_id)
     return render_to_response('performer_movie.html',{'user':user_id,'movies':movies,'person':performer},RequestContext(request))


def show_movies_of_directors(request, director_id):
    user_id=UserProfile.objects.get(email=request.user.username)
    movies=Movie_poster.objects.filter(movie__movie_director__director=director_id)
    director=Director.objects.get(pk=director_id)
    return render_to_response('performer_movie.html',{'user':user_id,'movies':movies,'person':director},RequestContext(request))


def recommend_movie_for_user(request):
    user_id=UserProfile.objects.get(email=request.user.username)
    movies=Movie_poster.objects.filter(movie__group_recommend_movie__group_id__user_in_group__user=user_id.id)
    return render_to_response('recommend_movie.html', {'user':user_id,'movies':movies}, RequestContext(request))

