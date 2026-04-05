from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "generic/404.html", status=404)

def custom_403(request, exception):
    return render(request, "generic/403.html", status=403)

def custom_500(request):
    return render(request, "generic/500.html", status=500)