from django.shortcuts import render
from django.http import HttpResponse

#from cassandra.cqlengine import connection
#from cassandra.cqlengine.management import sync_table
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import tuple_factory

# Create your views here.

def index(request):
    auth = PlainTextAuthProvider(username='', password='')
    cluster = Cluster([''], auth_provider=auth)
    session = cluster.connect('')
    session.row_factory = tuple_factory
    rows = session.execute("SELECT * FROM ")
    body = rows
    return HttpResponse(body)
