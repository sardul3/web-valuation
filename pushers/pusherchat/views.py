#render library for returning views to the browser
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#decorator to make a function only accessible to registered users
from django.contrib.auth.decorators import login_required
#import the user library
from pusher import Pusher
#replace the xxx with your app_id, key and secret respectively
#instantate the pusher class
# pusher = Pusher(app_id=u'763923', key=u'64cd546c6300e1f262be', secret=u'52d56fb58fac7d268800', cluster=u'us2')


import pusher

pusher = Pusher(
  app_id=u'763940',
  key=u'245a22748d5c8c572255',
  secret=u'1d4563819d5d4133edcd',
  cluster=u'us2',
)




@login_required(login_url='/admin/login/')
def chat(request):
    return render(request,"chat.html");


@csrf_exempt
def broadcast(request):
    pusher.trigger(u'a_channel', u'an_event', {u'name': request.user.username, u'message': request.POST['message']})
    return HttpResponse("done");
    print(pusher)
    print(request.POST['message'])
