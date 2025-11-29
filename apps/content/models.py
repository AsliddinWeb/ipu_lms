# apps/content/models.py

from django.db import models
from apps.courses.models import Course, Lesson


class Material(models.Model):
    """O'quv materiali"""

    class Type(models.TextChoices):
        PDF = 'pdf', 'PDF hujjat'
        VIDEO = 'video', 'Video'
        DOCUMENT = 'document', 'Hujjat (Word, Excel)'
        IMAGE = 'image', 'Rasm'
        LINK = 'link', 'Havola'
        ARCHIVE = 'archive', 'Arxiv (ZIP, RAR)'
        OTHER = 'other', 'Boshqa'

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name="Kurs"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
        verbose_name="Dars"
    )

    title = models.CharField(max_length=200, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    material_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.PDF,
        verbose_name="Turi"
    )

    file = models.FileField(
        upload_to='materials/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Fayl"
    )
    url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Havola"
    )

    file_size = models.PositiveIntegerField(default=0, verbose_name="Fayl hajmi (bytes)")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Yuklab olishlar")

    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiallar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Fayl hajmini o'qilishi oson formatda ko'rsatish"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def get_icon(self):
        """Material turiga qarab ikonka"""
        icons = {
            'pdf': 'bi-file-pdf text-danger',
            'video': 'bi-play-circle text-primary',
            'document': 'bi-file-word text-primary',
            'image': 'bi-file-image text-success',
            'link': 'bi-link-45deg text-info',
            'archive': 'bi-file-zip text-warning',
            'other': 'bi-file-earmark text-secondary',
        }
        return icons.get(self.material_type, icons['other'])