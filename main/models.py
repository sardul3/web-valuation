from django.db import models
from django.core.mail import send_mail

# Create your models here.


class Evaluator(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)

    def send_invite(self):
        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            [self.email],
            fail_silently=False,
        )
        self.save()

    def __str__(self):
        return self.name
