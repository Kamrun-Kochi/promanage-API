# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # অ্যাডমিন প্যানেলের লিস্টে কোন ফিল্ডগুলো দেখা যাবে
    list_display = ('email', 'username', 'is_staff', 'is_active')
    # ইমেল দিয়ে সার্চ করার সুবিধা
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    # নতুন ইউজার তৈরি বা এডিট করার সময় কোন ফিল্ডগুলো থাকবে
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'bio')}),
    )
