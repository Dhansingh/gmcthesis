from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="programs"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Student(models.Model):
    name = models.CharField(max_length=200)
    registration_number = models.CharField(
        max_length=100,
        unique=True
    )
    email = models.EmailField(blank=True)
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name="students"
    )
    batch = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.registration_number}"


class Supervisor(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=150, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="supervisors"
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ResearchArea(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Thesis(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PENDING", "Pending Approval"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    title = models.CharField(max_length=500)

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="theses"
    )

    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.PROTECT,
        related_name="theses"
    )

    research_area = models.ForeignKey(
        ResearchArea,
        on_delete=models.PROTECT,
        related_name="theses"
    )

    abstract = models.TextField()

    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        related_name="theses"
    )

    objectives = models.TextField(blank=True)

    methodology = models.TextField(blank=True)

    findings = models.TextField(blank=True)

    conclusion = models.TextField(blank=True)

    publication_year = models.CharField(
        max_length=20,
        help_text="Example: 2082 or 2025"
    )

    pages = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    thesis_file = models.FileField(
        upload_to="thesis/%Y/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf"]
            )
        ],
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    view_count = models.PositiveIntegerField(default=0)

    download_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # Future AI fields
    embedding_status = models.BooleanField(default=False)

    class Meta:
        ordering = ["-publication_year", "-created_at"]

    def __str__(self):
        return self.title

# Create your models here.
class LoginHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_history"
    )

    login_time = models.DateTimeField(
        auto_now_add=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["-login_time"]
        verbose_name = "Login History"
        verbose_name_plural = "Login History"

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
