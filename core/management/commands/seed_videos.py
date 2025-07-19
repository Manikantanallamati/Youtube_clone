# from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User
# from core.models import Video
# import random

# class Command(BaseCommand):
#     help = 'Seed database with random videos'

#     def handle(self, *args, **kwargs):
#         user = User.objects.first() 

#         titles = [
#             "Python Tutorial", "Django Basics", "Funny Cats", "Tech Review",
#             "Gadget Unboxing", "Space Documentary", "Music Video", "Travel Vlog"
#         ]

#         for i in range(10):
#             Video.objects.create(
#                 title=random.choice(titles) + f" #{i}",
#                 description="This is a sample video.",
#                 file="videos/sample.mp4", 
#                 uploaded_by=user,
#                 views=random.randint(100, 10000),
#                 category="Education"
#             )

#         self.stdout.write(self.style.SUCCESS("Dummy videos added successfully!"))
