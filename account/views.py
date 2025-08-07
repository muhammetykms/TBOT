from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from account.models import CustomUser

# Create your views here.


def login_request(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        
        email = request.POST["email"]
        password = request.POST["password"]


        if not email:
            context={
                    "email":"",
                    "sifre":""
                }
            return render(request, "account/login.html", {
                "error": "'E-mail alanı boş bırakılamaz."
            })
        
        if not password:
            context={
             "email":email,
             "sifre":""
                }
            return render(request, "account/login.html", {
                "error": "'Şifre' alanı boş bırakılamaz."
            })
            
            
        # Öncelikle email'ya göre kullanıcıyı sorgula
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None

        # Kullanıcı varsa ve şifre doğruysa oturum aç
        if user is not None and user.check_password(password):
            login(request, user)
            return redirect("home")
        else:
            return render(request, "account/login.html", {
                "error": "'E-mail', ya da 'parola' hatalı."
            })
    context={
             "email":"",
             "sifre":""
    }
    return render(request, "account/login.html",context)

def register_request(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        tel_no = request.POST["tel_no"]
        password = request.POST["password"]
        repassword = request.POST["repassword"]



        if password == repassword:
            if CustomUser.objects.filter(username=username).exists():
                return render(request, "account/register.html", {"error": "Bu TC No zaten kullanılıyor.!"})
            else:
                if CustomUser.objects.filter(email=email).exists():
                    return render(request, "account/register.html", {"error": "Bu email zaten kullanılıyor.!"})
                else:
                    user = CustomUser.objects.create_user(
                        username=username, 
                        first_name=first_name, 
                        last_name=last_name, 
                        tel_no=tel_no, 
                        email=email,  
                        password=password)
                    user.save()
                    return redirect("login")
        else:
            return render(request, "account/register.html", {"error": "Parolalar eşleşmiyor!"})

    return render(request, "account/register.html")

def logout_request(request):
    logout(request)
    return redirect("login")
