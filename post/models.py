from tabnanny import verbose

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels  # type: ignore
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        PUBLISHED = 'PB', 'انتشار'
        DRAFT = 'DF', 'پیش نویس'
        REJECTED = 'RJ', 'رد شده'

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts', verbose_name='نویسنده')

    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='جزئیات')
    slug = models.SlugField(max_length=200, verbose_name='اسلاگ')

    publish = jmodels.jDateTimeField(
        default=timezone.now, verbose_name='تاریخ انتشار')
    created = jmodels.jDateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated = jmodels.jDateTimeField(
        auto_now=True, verbose_name='تاریخ ویرایش')
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT,
                              verbose_name='وضعیت')
    reading_time = models.PositiveIntegerField(verbose_name='زمان مطالعه')

    objects = jmodels.jManager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post:post_detail', args=[self.id])


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OP', 'باز'
        CLOSE = 'CL', 'بسته'

    class Subject(models.TextChoices):
        PISHNAHAD = 'پیشنهاد', 'پیشنهاد'
        ENTGHAD = 'انتقاد', 'انتقاد'
        REPORT = 'گزارش', 'گزارش'

    name = models.CharField(max_length=30, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=11)
    title = models.CharField(max_length=52, verbose_name="عنوان")
    description = models.TextField(verbose_name="جزئیات")
    status = models.CharField(max_length=2, choices=Status.choices,
                              default=Status.OPEN, verbose_name="وضعیت")
    subject = models.CharField(max_length=10, verbose_name="موضوع",
                               choices=Subject.choices, default=Subject.PISHNAHAD)

    class Meta:
        ordering = ['-name']
        indexes = [
            models.Index(fields=['-name']),
        ]
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت ها'

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='پست')
    name = models.CharField(max_length=50, verbose_name="اسم")
    message = models.TextField(verbose_name="متن")
    created = jmodels.jDateTimeField(
        auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated = jmodels.jDateTimeField(
        auto_now=True, verbose_name='تاریخ ویرایش')
    active = models.BooleanField(verbose_name='نمایش', default=False)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'

    def __str__(self):
        return f"{self.name}: {self.post}"


class Image(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images", verbose_name="پست")
    title = models.CharField(
        max_length=150, verbose_name="عنوان", null=True, blank=True)
    description = models.TextField(
        verbose_name="جزئیات", null=True, blank=True)
    created = jmodels.jDateTimeField(
        auto_now_add=True, verbose_name="تاریخ ایجاد")
    image_file = models.ImageField(upload_to='post_images/')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = "تصویر"
        verbose_name_plural = "تصاویر"
