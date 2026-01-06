from django.db import models


class Homepage(models.Model):
    header = models.TextField(blank=True, verbose_name='Профессия')
    summary = models.TextField(blank=True, verbose_name='Описание')
    banner_image = models.ImageField(blank=False, verbose_name='Баннер', upload_to='uploads/')


class HomepageImage(models.Model):
    homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name='extra_images',
                                 verbose_name='Главная страница')
    image = models.ImageField(verbose_name='Дополнительные изображения', upload_to='uploads/')


class JobDemand(models.Model):
    salary_graph = models.ImageField(blank=False, verbose_name='График зарплат')
    vacancy_graph = models.ImageField(blank=False, verbose_name='График вакансий')
    salary_table = models.TextField(blank=False, verbose_name='Таблица зарплат')
    vacancy_table = models.TextField(blank=False, verbose_name='Таблица вакансий')


class RegionData(models.Model):
    city_salary_graph = models.ImageField(blank=False, verbose_name='График зарплат по городам')
    city_vacancy_graph = models.ImageField(blank=False, verbose_name='График вакансий по городам')
    city_salary_table = models.TextField(blank=False, verbose_name='Таблица зарплат по городам')
    city_vacancy_table = models.TextField(blank=False, verbose_name='Таблица вакансий по городам')


class Skillset(models.Model):
    table_header = models.TextField(blank=False, verbose_name='Название таблицы', max_length=30)
    skill_table = models.TextField(blank=False, verbose_name='Таблица скиллов')
    skill_graph = models.ImageField(blank=False, verbose_name='График скиллов')

    class Meta:
        verbose_name = 'skill'
        verbose_name_plural = 'skills'


class StatisticalData(models.Model):
    yearly_salary_graph = models.ImageField(blank=False, verbose_name='График зарплат по годам')
    yearly_salary_table = models.TextField(blank=False, verbose_name='Таблица зарплат по годам')

    yearly_vacancy_graph = models.ImageField(blank=False, verbose_name='График вакансий по годам')
    yearly_vacancy_table = models.TextField(blank=False, verbose_name='Таблица вакансий по годам')

    city_salary_graph = models.ImageField(blank=False, verbose_name='График зарплат по городам')
    city_salary_table = models.TextField(blank=False, verbose_name='Таблица зарплат по городам')

    city_vacancy_graph = models.ImageField(blank=False, verbose_name='График вакансий по городам')
    city_vacancy_table = models.TextField(blank=False, verbose_name='Таблица вакансий по городам')

    skill_top20_graph = models.ImageField(blank=False, verbose_name='График топ 20 навыков')
    skill_top20_table = models.TextField(blank=False, verbose_name='Таблица топ 20 навыков')
