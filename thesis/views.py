from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render,get_object_or_404
from urllib.parse import urlencode
import os
from django.db import models
from django.http import FileResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Thesis,
    Student,
    ResearchArea,
    Program,
)
def home(request):

    approved_theses = Thesis.objects.filter(
        status="APPROVED"
    )

    context = {
        "thesis_count": approved_theses.count(),

        "author_count": Student.objects.count(),

        "research_area_count": ResearchArea.objects.count(),

        "programs": Program.objects.filter(
            is_active=True
        ).prefetch_related("students"),

        "research_areas": ResearchArea.objects.all(),

        "recent_theses": approved_theses.select_related(
            "student",
            "research_area",
            "student__program",
        ).prefetch_related(
            "keywords"
        )[:6],
    }

    return render(
        request,
        "home.html",
        context
    )


# =========================================================
# THESIS BROWSE PAGE
# =========================================================

# =========================================================
# ADVANCED THESIS SEARCH
# =========================================================
from urllib.parse import urlencode
@login_required(login_url="login")
def thesis_list(request):

    theses = (
        Thesis.objects
        .filter(status="APPROVED")
        .select_related(
            "student",
            "student__program",
            "research_area",
        )
        .prefetch_related(
            "keywords"
        )
    )

    # =====================================================
    # GET SEARCH PARAMETERS
    # =====================================================

    query = request.GET.get("q", "").strip()

    author = request.GET.get("author", "").strip()

    keyword = request.GET.get("keyword", "").strip()

    abstract = request.GET.get("abstract", "").strip()

    search_in = request.GET.get(
        "search_in",
        "all"
    ).strip()

    match_mode = request.GET.get(
        "match",
        "all"
    ).strip()

    program = request.GET.get(
        "program",
        ""
    ).strip()

    area = request.GET.get(
        "area",
        ""
    ).strip()

    year = request.GET.get(
        "year",
        ""
    ).strip()

    from_year = request.GET.get(
        "from_year",
        ""
    ).strip()

    to_year = request.GET.get(
        "to_year",
        ""
    ).strip()

    sort = request.GET.get(
        "sort",
        "newest"
    ).strip()


    # =====================================================
    # ADVANCED KEYWORD SEARCH
    # =====================================================

    if query:

        # Remove surrounding quotes if user searches:
        # "commercial bank profitability"

        if (
            len(query) >= 2
            and query.startswith('"')
            and query.endswith('"')
        ):
            query = query[1:-1].strip()


        # Split search into individual words

        search_terms = query.split()


        # -------------------------------------------------
        # Fields to search
        # -------------------------------------------------

        if search_in == "title":

            search_fields = [
                "title__icontains"
            ]

        elif search_in == "abstract":

            search_fields = [
                "abstract__icontains"
            ]

        elif search_in == "author":

            search_fields = [
                "student__name__icontains"
            ]

        elif search_in == "keyword":

            search_fields = [
                "keywords__name__icontains"
            ]

        else:

            search_fields = [
                "title__icontains",
                "abstract__icontains",
                "student__name__icontains",
                "research_area__name__icontains",
                "keywords__name__icontains",
            ]


        # -------------------------------------------------
        # ALL WORDS
        # -------------------------------------------------

        if match_mode == "all":

            for term in search_terms:

                term_query = Q()

                for field in search_fields:

                    term_query |= Q(
                        **{field: term}
                    )

                theses = theses.filter(
                    term_query
                )


        # -------------------------------------------------
        # ANY WORD
        # -------------------------------------------------

        else:

            term_query = Q()

            for term in search_terms:

                for field in search_fields:

                    term_query |= Q(
                        **{field: term}
                    )

            theses = theses.filter(
                term_query
            )


    # =====================================================
    # AUTHOR FILTER
    # =====================================================

    if author:

        theses = theses.filter(
            student__name__icontains=author
        )


    # =====================================================
    # KEYWORD FILTER
    # =====================================================

    if keyword:

        theses = theses.filter(
            keywords__name__icontains=keyword
        )


    # =====================================================
    # ABSTRACT FILTER
    # =====================================================

    if abstract:

        theses = theses.filter(
            abstract__icontains=abstract
        )


    # =====================================================
    # PROGRAM FILTER
    # =====================================================

    if program:

        theses = theses.filter(
            student__program__code__iexact=program
        )


    # =====================================================
    # RESEARCH AREA FILTER
    # =====================================================

    if area:

        theses = theses.filter(
            research_area__id=area
        )


    # =====================================================
    # EXACT YEAR
    # =====================================================

    if year:

        theses = theses.filter(
            publication_year=year
        )


    # =====================================================
    # YEAR RANGE
    # =====================================================

    if from_year:

        theses = theses.filter(
            publication_year__gte=from_year
        )


    if to_year:

        theses = theses.filter(
            publication_year__lte=to_year
        )


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    theses = theses.distinct()


    # =====================================================
    # SORTING
    # =====================================================

    if sort == "oldest":

        theses = theses.order_by(
            "publication_year",
            "id"
        )

    elif sort == "title":

        theses = theses.order_by(
            "title"
        )

    elif sort == "author":

        theses = theses.order_by(
            "student__name"
        )

    else:

        theses = theses.order_by(
            "-publication_year",
            "-id"
        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        theses,
        9
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    # =====================================================
    # AVAILABLE YEARS
    # =====================================================

    years = (
        Thesis.objects
        .filter(status="APPROVED")
        .values_list(
            "publication_year",
            flat=True
        )
        .distinct()
        .order_by("-publication_year")
    )

    # =====================================================
    # PAGINATION QUERY STRING
    # =====================================================

    pagination_params = request.GET.copy()

    if "page" in pagination_params:

        del pagination_params["page"]

    pagination_query = pagination_params.urlencode()   
    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "page_obj": page_obj,

        "theses": page_obj.object_list,

        # Search
        "query": query,

        "author": author,

        "keyword": keyword,

        "abstract": abstract,

        "search_in": search_in,

        "match_mode": match_mode,

        # Filters
        "selected_program": program,

        "selected_area": area,

        "selected_year": year,

        "from_year": from_year,

        "to_year": to_year,

        "sort": sort,

        # Options
        "programs": Program.objects.filter(
            is_active=True
        ),

        "research_areas": ResearchArea.objects.all(),

        "years": years,

        # Result information
        "total_results": paginator.count,
        "pagination_query": pagination_query,

    }


    return render(
        request,
        "thesis_list.html",
        context
    )

    Theses= Thesis.objects.filter(
        status="APPROVED"
    ).select_related(
        "student",
        "student__program",
        "research_area",
    ).prefetch_related(
        "keywords"
    ).order_by(
        "-publication_year",
        "-id"
    )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    query = request.GET.get("q", "").strip()

    if query:

        theses = theses.filter(
            Q(title__icontains=query)
            |
            Q(abstract__icontains=query)
            |
            Q(student__name__icontains=query)
            |
            Q(research_area__name__icontains=query)
            |
            Q(keywords__name__icontains=query)
        ).distinct()


    # -----------------------------------------------------
    # PROGRAM FILTER
    # -----------------------------------------------------

    program = request.GET.get(
        "program",
        ""
    ).strip()

    if program:

        theses = theses.filter(
            student__program__code__iexact=program
        )


    # -----------------------------------------------------
    # RESEARCH AREA FILTER
    # -----------------------------------------------------

    area = request.GET.get(
        "area",
        ""
    ).strip()

    if area:

        theses = theses.filter(
            research_area__id=area
        )


    # -----------------------------------------------------
    # YEAR FILTER
    # -----------------------------------------------------

    year = request.GET.get(
        "year",
        ""
    ).strip()

    if year:

        theses = theses.filter(
            publication_year=year
        )


    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    paginator = Paginator(
        theses,
        9
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    # -----------------------------------------------------
    # YEARS
    # -----------------------------------------------------

    years = (
        Thesis.objects
        .filter(
            status="APPROVED"
        )
        .values_list(
            "publication_year",
            flat=True
        )
        .distinct()
        .order_by(
            "-publication_year"
        )
    )


    context = {

        "page_obj": page_obj,

        "theses": page_obj.object_list,

        "query": query,

        "selected_program": program,

        "selected_area": area,

        "selected_year": year,

        "programs": Program.objects.filter(
            is_active=True
        ),

        "research_areas": ResearchArea.objects.all(),

        "years": years,

        "total_results": paginator.count,

    }


    return render(
        request,
        "thesis_list.html",
        context
    )
# =========================================================
# THESIS DETAIL PAGE
# =========================================================
@login_required(login_url="login")
def thesis_detail(request, pk):

    # -----------------------------------------------------
    # GET ONLY APPROVED THESIS
    # -----------------------------------------------------

    thesis = get_object_or_404(
        Thesis.objects
        .filter(status="APPROVED")
        .select_related(
            "student",
            "student__program",
            "research_area",
        )
        .prefetch_related(
            "keywords"
        ),
        pk=pk
    )


    # -----------------------------------------------------
    # RELATED THESIS
    # -----------------------------------------------------

    related_theses = Thesis.objects.filter(
        status="APPROVED"
    ).exclude(
        pk=thesis.pk
    ).select_related(
        "student",
        "student__program",
        "research_area",
    ).prefetch_related(
        "keywords"
    )


    # -----------------------------------------------------
    # PRIORITIZE SAME RESEARCH AREA
    # -----------------------------------------------------

    if thesis.research_area:

        same_area = related_theses.filter(
            research_area=thesis.research_area
        )[:3]

    else:

        same_area = related_theses[:3]


    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    if same_area.count() < 3:

        existing_ids = list(
            same_area.values_list(
                "id",
                flat=True
            )
        )

        extra_theses = related_theses.exclude(
            id__in=existing_ids
        )[:3 - same_area.count()]

        related_theses = list(same_area) + list(extra_theses)

    else:

        related_theses = list(same_area)


    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        "thesis": thesis,

        "related_theses": related_theses,

    }


    return render(
        request,
        "thesis_detail.html",
        context
    )
# =========================================================
# READ THESIS PDF
# =========================================================
@login_required(login_url="login")
def read_thesis(request, pk):

    thesis = get_object_or_404(
        Thesis.objects.select_related(
            "student",
            "student__program",
            "research_area",
        ),
        pk=pk,
        status="APPROVED",
    )

    # Check whether PDF exists
    if not thesis.thesis_file:
        raise Http404("Thesis PDF is not available.")

    # Check physical file
    try:
        file_handle = thesis.thesis_file.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404("Thesis PDF file could not be found.")

    # Increase view count
    Thesis.objects.filter(pk=pk).update(
        view_count=models.F("view_count") + 1
    )

    filename = os.path.basename(
        thesis.thesis_file.name
    )

    response = FileResponse(
        file_handle,
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'inline; filename="{filename}"'
    )

    return response


# =========================================================
# DOWNLOAD THESIS PDF
# =========================================================
@login_required(login_url="login")
def download_thesis(request, pk):

    thesis = get_object_or_404(
        Thesis.objects.select_related(
            "student",
            "student__program",
            "research_area",
        ),
        pk=pk,
        status="APPROVED",
    )

    # Check whether PDF exists
    if not thesis.thesis_file:
        raise Http404("Thesis PDF is not available.")

    # Check physical file
    try:
        file_handle = thesis.thesis_file.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404("Thesis PDF file could not be found.")

    # Increase download count
    Thesis.objects.filter(pk=pk).update(
        download_count=models.F("download_count") + 1
    )

    filename = os.path.basename(
        thesis.thesis_file.name
    )

    response = FileResponse(
        file_handle,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )

    return response

def thesis_detail(request, pk):

    thesis = get_object_or_404(
        Thesis.objects
        .filter(status="APPROVED")
        .select_related(
            "student",
            "student__program",
            "student__program__department",
            "supervisor",
            "research_area",
        )
        .prefetch_related(
            "keywords"
        ),
        pk=pk
    )

    # ---------------------------------------------------------
    # RELATED THESES
    # ---------------------------------------------------------

    related_theses = (
        Thesis.objects
        .filter(
            status="APPROVED",
            research_area=thesis.research_area,
        )
        .exclude(pk=thesis.pk)
        .select_related(
            "student",
            "student__program",
        )
        .prefetch_related(
            "keywords"
        )
        .order_by("-publication_year", "-created_at")[:3]
    )

    # ---------------------------------------------------------
    # PAGE CONTEXT
    # ---------------------------------------------------------

    context = {
        "thesis": thesis,
        "related_theses": related_theses,
    }

    # ---------------------------------------------------------
    # RETURN PAGE
    # ---------------------------------------------------------

    return render(
        request,
        "thesis_detail.html",
        context
    )
def user_login(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # -------------------------------------------------
            # RECORD LOGIN
            # -------------------------------------------------

            from .models import LoginHistory

            ip_address = (
                request.META.get("HTTP_X_FORWARDED_FOR")
                or request.META.get("REMOTE_ADDR")
            )

            if ip_address and "," in ip_address:
                ip_address = ip_address.split(",")[0].strip()

            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=request.META.get(
                    "HTTP_USER_AGENT",
                    ""
                )
            )

            return redirect(
                request.GET.get(
                    "next",
                    "home"
                )
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "registration/login.html"
    )
def user_logout(request):

    logout(request)

    return redirect("login")
def user_register(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not username:
            messages.error(
                request,
                "Username is required."
            )

            return render(
                request,
                "registration/register.html"
            )


        # -------------------------------------------------
        # CHECK USERNAME
        # -------------------------------------------------

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "This username already exists. Please choose another username."
            )

            return render(
                request,
                "registration/register.html"
            )


        # -------------------------------------------------
        # CHECK EMAIL
        # -------------------------------------------------

        if email and User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "This email address is already registered."
            )

            return render(
                request,
                "registration/register.html"
            )


        # -------------------------------------------------
        # PASSWORD CHECK
        # -------------------------------------------------

        if len(password) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return render(
                request,
                "registration/register.html"
            )


        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "registration/register.html"
            )


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )


        # -------------------------------------------------
        # AUTOMATIC LOGIN
        # -------------------------------------------------

        login(
            request,
            user
        )


        # -------------------------------------------------
        # LOGIN HISTORY
        # -------------------------------------------------

        from .models import LoginHistory

        ip_address = (
            request.META.get("HTTP_X_FORWARDED_FOR")
            or request.META.get("REMOTE_ADDR")
        )

        if ip_address and "," in ip_address:

            ip_address = (
                ip_address
                .split(",")[0]
                .strip()
            )

        LoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=request.META.get(
                "HTTP_USER_AGENT",
                ""
            )
        )


        messages.success(
            request,
            "Your account has been created successfully."
        )

        return redirect("home")


    return render(
        request,
        "registration/register.html"
    )