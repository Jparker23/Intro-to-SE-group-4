from django.shortcuts import render,redirect 
from .forms import ProductForm
#this page is pretty much all render requests to load my HTML templates and returns a HttpResponse


def home(request):
    return render(request, "generic/home.html")

def brandResults(request, brand):
    return render(request, "generic/brandResults.html", {"brand": brand})
def catalog(request):
    return render(request, "generic/catalog.html")


def adminModeration(request):
    return render(request, "generic/adminModeration.html")


def billing(request):
    return render(request, "generic/billing.html")

def orderConf(request):
    return render(request, "generic/orderConf.html")


def orders(request):
    return render(request, "generic/orders.html")

def addresses(request):
    return render(request, "generic/addresses.html")

def returnReq(request):
    return render(request, "generic/returnReq.html")

def returns(request):
    return render(request, "generic/returns.html")



def createProd(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Check whether it's valid and save the data
            form.save()
            #html page for sellers will be created then linked to this
            return redirect('')
    else:
        # any other request method creates an empty form
        form = ProductForm()
        
    # pull up html page- needs to be named
    return render(request, '', {'form': form})