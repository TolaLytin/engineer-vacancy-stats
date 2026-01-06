from datetime import datetime

import requests
from django.shortcuts import render

from . import utils
from .models import *
from .context_helpers import *


def home(request):
    return render(request, 'home.html', {
        'context': homepage_content(request)
    })


def stats(request):
    stats = StatisticalData.objects.first()

    return render(request, 'statistics.html', {
        'salary_chart': stats.yearly_salary_graph.url,
        'salary_data': stats.yearly_salary_table,
        'vacancy_chart': stats.yearly_vacancy_graph.url,
        'vacancy_data': stats.yearly_vacancy_table,
        'city_salary_chart': stats.city_salary_graph.url,
        'city_salary_data': stats.city_salary_table,
        'city_vacancy_chart': stats.city_vacancy_graph.url,
        'city_vacancy_data': stats.city_vacancy_table,
        'skill_chart': stats.skill_top20_graph.url,
        'skill_data': stats.skill_top20_table
    })


def job_demand(request):
    demand = JobDemand.objects.first()

    return render(request, 'job_demand.html', {
        'salary_graph': demand.salary_graph.url,
        'vacancy_graph': demand.vacancy_graph.url,
        'salary_data': demand.salary_table,
        'vacancy_data': demand.vacancy_table
    })


def regions(request):
    region_info = RegionData.objects.first()

    return render(request, 'regions.html', {
        'city_salary_graph': region_info.city_salary_graph.url,
        'city_vacancy_graph': region_info.city_vacancy_graph.url,
        'city_salary_table': region_info.city_salary_table,
        'city_vacancy_table': region_info.city_vacancy_table
    })


def skills_overview(request):
    skills = skills_page_content(request).first()

    return render(request, 'skills.html', {
        'skill_chart': skills.skill_graph.url,
        'skill_table': skills.skill_table
    })


def recent_jobs(request):
    keywords = ['developer', 'инженер-программист', 'разработчик']
    search_query = ', '.join(keywords)

    api_url = 'https://api.hh.ru/vacancies/'
    params = {
        'period': 1,
        'page': 0,
        'per_page': 10,
        'text': search_query
    }

    response = requests.get(api_url, params=params)
    jobs = response.json().get('items', [])

    detailed_jobs = []
    for job in jobs:
        job_details = requests.get(f"https://api.hh.ru/vacancies/{job['id']}").json()

        skills = ', '.join([skill['name'] for skill in job_details.get('key_skills', [])])
        description = job_details.get('description', 'Нет описания')

        salary = job_details['salary']
        salary_str = ''

        if salary:
            salary = utils.process_salary(salary)
            if salary['from'] and salary['to']:
                salary_str = f"{salary['from']} - {salary['to']}"
            elif salary['from']:
                salary_str = f"{salary['from']}"
            elif salary['to']:
                salary_str = f"{salary['to']}"
        else:
            salary_str = 'Не указана'

        detailed_jobs.append({
            'title': job_details['name'],
            'description': utils.strip_html(description),
            'skills': skills,
            'company': job_details['employer']['name'],
            'salary': salary_str,
            'location': job_details['area']['name'],
            'date_posted': job_details['published_at'],
        })

    detailed_jobs.sort(key=lambda x: datetime.strptime(x['date_posted'], "%Y-%m-%dT%H:%M:%S%z"), reverse=True)

    for job in detailed_jobs:
        job['date_posted'] = utils.format_date(job['date_posted'])

    return render(request, 'recent_jobs.html', {
        'jobs': detailed_jobs
    })
