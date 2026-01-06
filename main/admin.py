from django.contrib import admin
from .models import Homepage, HomepageImage, JobDemand, RegionData, Skillset, StatisticalData


class HomepageImageInline(admin.TabularInline):
    model = HomepageImage
    extra = 1


@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    inlines = [HomepageImageInline]


admin.site.register(JobDemand)
admin.site.register(RegionData)
admin.site.register(Skillset)
admin.site.register(StatisticalData)
