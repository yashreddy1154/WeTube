
from django.contrib import admin
from .models import CustomUser

# This makes your custom user show up in the Django admin dashboard
admin.site.register(CustomUser)
