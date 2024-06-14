from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)  # Assuming mobile numbers can be up to 15 characters long
    location = models.CharField(max_length=255)  # Assuming location names can be up to 255 characters long

    def __str__(self):
        return self.name
