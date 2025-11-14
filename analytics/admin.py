from django.contrib import admin
from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('get_page_info', 'raffle', 'ip_address', 'viewed_at')
    list_filter = ('page_type', 'raffle', 'viewed_at', 'country')
    search_fields = ('ip_address', 'raffle__name', 'user_agent')
    readonly_fields = ('viewed_at', 'user_agent', 'ip_address', 'referer', 'country')
    date_hierarchy = 'viewed_at'
    
    def get_page_info(self, obj):
        return f"{obj.get_page_type_display()}"
    get_page_info.short_description = 'Página'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
