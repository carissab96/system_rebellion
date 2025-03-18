from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SystemMetrics, OptimizationProfile, OptimizationResult, SystemAlert, UserProfile, UserPreferences, AutoTuner, AutoTuningResult

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserPreferencesInline(admin.StackedInline):
    model = UserPreferences
    can_delete = False
    verbose_name_plural = 'Preferences'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, UserPreferencesInline)
    list_display = ('username', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name')}),
        ('System Info', {'fields': ('system_id', 'optimization_preferences')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'system_id')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'operating_system', 'os_version')
    list_filter = ('operating_system',)
    search_fields = ('user__username', 'operating_system')

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('optimization_level',)
    list_filter = ('optimization_level',)

@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'cpu_usage', 'memory_usage', 'disk_usage')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)

@admin.register(OptimizationProfile)
class OptimizationProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

@admin.register(OptimizationResult)
class OptimizationResultAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'success')
    list_filter = ('success', 'timestamp')
    ordering = ('-timestamp',)

@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'title', 'severity', 'is_read')
    list_filter = ('severity', 'is_read', 'timestamp')
    search_fields = ('title', 'message')
    ordering = ('-timestamp',)

@admin.register(AutoTuner)
class AutoTunerAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'profile', 'success')
    list_filter = ('success', 'timestamp')
    ordering = ('-timestamp',)

@admin.register(AutoTuningResult)
class AutoTuningResultAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'success')
    list_filter = ('success', 'timestamp')
    ordering = ('-timestamp',)

