from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    )

class UserProfile(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    birthday = models.DateField()
    gender = models.CharField(max_length=1, choices = GENDER_CHOICES)
    email = models.EmailField(unique=True)
    create_time = models.DateTimeField()

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class Friendship(models.Model):
    friend_one = models.ForeignKey(UserProfile,related_name='friendshipsAsFirst')
    friend_two = models.ForeignKey(UserProfile,related_name='friendshipsAsSecond')
    time = models.DateTimeField()

    def __unicode__(self):
        return u'%s <-> %s' % (self.friend_one,self.friend_two)

    class Meta:
        unique_together=("friend_one","friend_two")

class Status(models.Model):
    user = models.ForeignKey(UserProfile)
    content = models.CharField(max_length=1000)
    time = models.DateTimeField()

    def __unicode__(self):
        return self.user

    class Meta:
        unique_together=("user","time")

class Message(models.Model):
    from_who = models.ForeignKey(UserProfile, related_name='messagesFromWho')
    to_who = models.ForeignKey(UserProfile, related_name='messagesToWho')
    content = models.CharField(max_length=1000)
    time = models.DateTimeField()

    def __unicode__(self):
        return u'%s says to %s' % (self.from_who, self.to_who)

    class Meta:
        unique_together=("from_who","to_who","time")

class Request(models.Model):
    from_who = models.ForeignKey(UserProfile, related_name='requestFromWho')
    to_who = models.ForeignKey(UserProfile, related_name='requestToWho')
    message = models.CharField(max_length=500)
    time = models.DateTimeField()

    def __unicode__(self):
        return u'%s request to be friends with %s' % (self.from_who, self.to_who)


class Movie(models.Model):
    mid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250, unique=True)
    year = models.SmallIntegerField()

    def __unicode__(self):
        return u'%s' % self.title

class Performer(models.Model):
    pid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)
    gender = models.CharField(max_length=1)

    def __unicode__(self):
        return u'%s' % self.name

class Director(models.Model):
    did = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)

    def __unicode__(self):
        return u'%s' % self.name

class Producer(models.Model):
    pid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)

    def __unicode__(self):
        return u'%s' % self.name

class Editor(models.Model):
    eid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)

    def __unicode__(self):
        return u'%s' % self.name

class Movie_role(models.Model):
    performer = models.ForeignKey(Performer)
    movie = models.ForeignKey(Movie)
    role=models.CharField(max_length=250, null=True)
    credit=models.SmallIntegerField(null=True)

    def __unicode__(self):
        return u'%s plays in %s as %s' % (self.performer, self.movie, self.role)

    class Meta:
        unique_together=("movie","performer","role")

class Movie_director(models.Model):
    movie = models.ForeignKey(Movie)
    director = models.ForeignKey(Director)

    def __unicode__(self):
        return u'%s directed %s' % (self.director, self.movie)

    class Meta:
        unique_together=("movie","director")

class Movie_producer(models.Model):
    movie = models.ForeignKey(Movie)
    producer = models.ForeignKey(Producer)

    def __unicode__(self):
        return u'%s produced %s' % (self.producer, self.movie)

    class Meta:
        unique_together=("movie","producer")


class Movie_editor(models.Model):
    movie = models.ForeignKey(Movie)
    editor = models.ForeignKey(Editor)

    def __unicode__(self):
        return u'%s write the script of %s' % (self.editor, self.movie)
    class Meta:
        unique_together=("movie","editor")

class Movie_rating(models.Model):
    movie = models.ForeignKey(Movie)
    rating =models.DecimalField(max_digits=2,decimal_places=1)
    vote = models.IntegerField()

    def __unicode__(self):
        return u'%s : %s' % (self.movie, self.rating)
    class Meta:
        unique_together=("movie","rating")

class Movie_genre(models.Model):
    movie = models.ForeignKey(Movie)
    genre = models.CharField(max_length=30)

    def __unicode__(self):
        return u'%s : %s' % (self.movie, self.genre)
    class Meta:
        unique_together=("movie","genre")

class Movie_runtime(models.Model):
    movie=models.ForeignKey(Movie)
    country = models.CharField(max_length=100,null=True)
    runtime = models.SmallIntegerField()

    def __unicode__(self):
        return u'%s runtime is %s' % (self.movie, self.runtime)
    class Meta:
        unique_together=("movie","country")

class Movie_keyword(models.Model):
    movie=models.ForeignKey(Movie)
    keyword=models.CharField(max_length=50)

    class Meta:
        unique_together=("movie","keyword")

class Movie_poster(models.Model):
    movie=models.ForeignKey(Movie, unique=True)
    thumbnail = models.URLField(null=True)
    profile = models.URLField(null=True)
    detailed = models.URLField(null=True)
    original = models.URLField(null=True)

class Movie_certificate(models.Model):
    movie=models.ForeignKey(Movie)
    country=models.CharField(max_length=100)
    certificate = models.CharField(max_length=50)

    class Meta:
        unique_together=("movie","country","certificate")

class Movie_review(models.Model):
    movie=models.ForeignKey(Movie)
    critic = models.CharField(max_length=100, null=True)
    time = models.DateField(null=True)
    freshness = models.CharField(max_length=20, null=True)
    publication= models.CharField(max_length=100, null=True)
    quote=models.CharField(max_length=500,null=True)
    link=models.CharField(max_length=200,null=True)

    class Meta:
        unique_together=("movie","critic","time")


class User_rating_and_review(models.Model):
    movie=models.ForeignKey(Movie)
    user=models.ForeignKey(UserProfile)
    rating=models.DecimalField(max_digits=2,decimal_places=1)
    review=models.CharField(max_length=20000, null=True)
    time = models.DateTimeField(null=True)

    class Meta:
        unique_together=("movie","user")

class Comment_to_rating_and_review(models.Model):
    review = models.ForeignKey(User_rating_and_review)
    from_who = models.ForeignKey(UserProfile,related_name='comment_From_Who')
    to_who = models.ForeignKey(UserProfile, related_name='comment_to_who')
    comment=models.CharField(max_length=5000)
    time = models.DateTimeField()


class Content_base_recommend_movie(models.Model):
    movie = models.ForeignKey(Movie, related_name='rated_movie')
    recommend_movie=models.ForeignKey(Movie, related_name='rec_movie')

class User_group(models.Model):
    group_id = models.SmallIntegerField(primary_key=True)

class Group_recommend_movie(models.Model):
    group_id = models.ForeignKey(User_group)
    movie = models.ForeignKey(Movie)

class User_in_group(models.Model):
    group_id = models.ForeignKey(User_group)
    user = models.ForeignKey(UserProfile)









