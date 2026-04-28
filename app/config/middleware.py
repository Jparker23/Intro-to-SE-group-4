from django.http import HttpResponseForbidden

#On the render deploy page bots are constantly trying to spam our pages so im trying to restrict this-madee

class BlockBadBotsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        bad_paths = [ "/wp-admin",
            "/wordpress",
            "/wp-login.php",
            "/xmlrpc.php",
            "/.env",
            "/phpmyadmin",
            "/admin.php",]

        if any(request.path.startswith(p) for p in bad_paths):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden()

        return self.get_response(request)