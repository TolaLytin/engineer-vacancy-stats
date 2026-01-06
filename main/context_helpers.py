from . import app_constants
from .models import *


def fetch_constants(request):
    return {'FC_DETAILS': app_constants.FC_DETAILS}


def academic_group_info(request):
    return {'GROUP_NAME': app_constants.GROUP_NAME}


def homepage_content(request):
    return Homepage.objects.prefetch_related('extra_images').all()


def skills_page_content(request):
    return Skillset.objects.all()


def profession_label(request):
    return {'PROF_LABEL': app_constants.PROF_LABEL}


def website_name(request):
    return {'WEBSITE_TITLE': app_constants.WEBSITE_TITLE}
