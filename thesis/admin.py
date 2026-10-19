from django.contrib import admin
from django.contrib import admin
from .models import LoginHistory
from .models import (
    Department,
    Program,
    Student,
    Supervisor,
    ResearchArea,
    Keyword,
    Thesis,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("name", "code")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "registration_number",
        "program",
        "batch",
    )
    list_filter = ("program", "batch")
    search_fields = (
        "name",
        "registration_number",
    )


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "designation",
        "department",
        "is_active",
    )
    list_filter = ("department", "is_active")
    search_fields = ("name",)


@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "student",
        "supervisor",
        "research_area",
        "publication_year",
        "status",
    )

    list_filter = (
        "status",
        "research_area",
        "publication_year",
    )

    search_fields = (
        "title",
        "abstract",
        "student__name",
        "student__registration_number",
        "supervisor__name",
        "keywords__name",
    )

    filter_horizontal = ("keywords",)

    readonly_fields = (
        "view_count",
        "download_count",
        "created_at",
        "updated_at",
    )

    # Allow editing existing thesis
    fields = (
        "title",
        "student",
        "supervisor",
        "research_area",
        "abstract",
        "keywords",
        "objectives",
        "methodology",
        "findings",
        "conclusion",
        "publication_year",
        "pages",
        "thesis_file",
        "status",
        "view_count",
        "download_count",
        "created_at",
        "updated_at",
    )
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "login_time",
        "ip_address",
        "short_user_agent",
    )

    list_filter = (
        "login_time",
    )

    search_fields = (
        "user__username",
        "user__email",
        "ip_address",
    )

    readonly_fields = (
        "user",
        "login_time",
        "ip_address",
        "user_agent",
    )

    ordering = (
        "-login_time",
    )

    def short_user_agent(self, obj):

        if not obj.user_agent:
            return "-"

        return obj.user_agent[:80]    