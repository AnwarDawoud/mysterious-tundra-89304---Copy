# hotel_your_choice/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import Hotel, Booking, CustomUser, Rating, Amenity, Photo
from django.contrib.auth.models import Group


class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'is_hotel_manager', 'is_client_user', 'is_administrator']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Roles', {'fields': ('is_hotel_manager', 'is_client_user', 'is_administrator')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_hotel_manager', 'is_client_user', 'is_administrator')}
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)

# Assuming you have a 'Hotel Managers' group and a 'Users' group
hotel_managers_group, created = Group.objects.get_or_create(name='Hotel Managers')
users_group, created = Group.objects.get_or_create(name='Users')

class ReschedulingStatusFilter(admin.SimpleListFilter):
    title = 'Rescheduling Status'
    parameter_name = 'rescheduling_status'

    def lookups(self, request, model_admin):
        return Booking.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'hotel',
        'check_in_date',
        'check_out_date',
        'booking_status_display'
    )
    list_filter = ('status', 'hotel')
    search_fields = ('id', 'user__username', 'hotel__name')

    def booking_status_display(self, obj):
        if obj.status == 'active':
            return format_html('<span class="booking-active">Booking Active</span>')
        elif obj.status == 'canceled':
            canceled_by_display = f' by {obj.canceled_by.username}' if obj.canceled_by else ' by USER ID#'
            return format_html('<span class="booking-canceled">Booking Canceled{}</span>', canceled_by_display)
        elif obj.status == 'rescheduled':
            if obj.original_booking:
                original_booking = obj.original_booking
                return format_html('<span class="booking-rescheduled">Booking Rescheduled from ID#{0}</span>', original_booking.id)
            else:
                return format_html('<span class="booking-rescheduled">Booking Rescheduled (Original Booking Missing)</span>')
        else:
            return ''

    booking_status_display.short_description = 'Booking Status'

    class Media:
        css = {
            'all': ('hotel_your_choice_css/admin_styles.css',),
        }


admin.site.register(Booking, BookingAdmin)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_booking', 'rating', 'text', 'timestamp')

    def get_booking(self, obj):
        return obj.booking

    get_booking.short_description = 'Booking'




class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'night_rate', 'address', 'display_amenities', 'display_other_photos')

    def display_amenities(self, obj):
        # Convert amenities string to a list for display
        return ', '.join(obj.amenities.split(', '))

    display_amenities.short_description = 'Amenities'

    def display_other_photos(self, obj):
        return ', '.join(photo.image.url for photo in obj.other_photos.all())

    display_other_photos.short_description = 'Other Photos'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        obj = self.get_object(request, object_id)

        amenities_link = format_html('<a href="{}?hotels__id__exact={}">{}</a>',
                                     reverse('admin:hotel_your_choice_amenity_changelist'), obj.id, obj.amenities)

        extra_context['amenities_link'] = amenities_link
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(Hotel, HotelAdmin)
admin.site.register(Amenity)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'image')


admin.site.register(Photo, PhotoAdmin)



