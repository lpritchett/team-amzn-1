# Create your models here.
from django.db import models


class Notification(models.Model):
    notificationid = models.IntegerField(db_column='notificationId', primary_key=True)  # Field name made lowercase.
    sentimentvalue = models.FloatField(db_column='sentimentValue')  # Field name made lowercase.
    email = models.CharField(max_length=45, blank=True)
    clusterN = models.ForeignKey('Cluster', db_column='cluster')

    class Meta:
        managed = False
        db_table = 'Notification'
        app_label = 'z'




class Cluster(models.Model):
    clusterid = models.IntegerField(db_column='clusterId', primary_key=True)  # Field name made lowercase.
    name = models.CharField(unique=True, max_length=32)
    ispinned = models.IntegerField(db_column='isPinned')  # Field name made lowercase.
    # notificationC = models.ForeignKey(Notification, db_column='notification', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clusters'
        app_label = 'x'

    def __str__(self):
        return '\nId: ' + self.clusterid.__str__() + '\nName: ' + self.name


class ClusterWord(models.Model):
    id = models.IntegerField(db_column='Id', primary_key=True)  # Field name made lowercase.
    word = models.CharField(max_length=45)
    clusterid = models.ForeignKey(Cluster, db_column='clusterId', blank=True, null=True)  # Field name made lowercase.
    count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ClusterWords'
        app_label = 'cw'


class Post(models.Model):
    postid = models.IntegerField(db_column='postId', primary_key=True)  # Field name made lowercase.
    threadid = models.IntegerField(db_column='threadId')  # Field name made lowercase.
    messageid = models.IntegerField(db_column='messageId')  # Field name made lowercase.
    forumid = models.IntegerField(db_column='forumId')  # Field name made lowercase.
    userid = models.IntegerField(db_column='userId')  # Field name made lowercase.
    categoryid = models.IntegerField(db_column='categoryId')  # Field name made lowercase.
    subject = models.CharField(max_length=512, blank=True)
    body = models.TextField(blank=True)
    postedbymoderator = models.IntegerField(db_column='postedByModerator')  # Field name made lowercase.
    resolutionstate = models.IntegerField(db_column='resolutionState')  # Field name made lowercase.
    helpfulanswer = models.IntegerField(db_column='helpfulAnswer')  # Field name made lowercase.
    correctanswer = models.IntegerField(db_column='correctAnswer')  # Field name made lowercase.
    username = models.CharField(db_column='userName', max_length=64)  # Field name made lowercase.
    userpoints = models.IntegerField(db_column='userPoints')  # Field name made lowercase.
    creationdate = models.DateField(db_column='creationDate')  # Field name made lowercase.
    modificationdate = models.DateField(db_column='modificationDate')  # Field name made lowercase.
    locale = models.CharField(max_length=64, blank=True)
    cluster = models.ForeignKey(Cluster, db_column='cluster', blank=True, null=True, on_delete=models.SET_NULL)
    stemmedbody = models.TextField(db_column='stemmedBody', blank=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'posts'
        app_label = 'y'

    def __str__(self):
        return self.subject + self.body


class Stopword(models.Model):
    id = models.IntegerField(db_column='Id')  # Field name made lowercase.
    word = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'StopWord'
        app_label = 'sw'

    def __str__(self):
        return self.word
