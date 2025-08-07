from django.shortcuts import redirect

def check_user_authenticated(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return func(request, *args, **kwargs)
    return wrapper

