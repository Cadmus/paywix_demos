from django.urls import path
from .views import home, payu_checkout, payu_failure, payu_success
                            


urlpatterns = [
    path('', home, name="home"),
    path('payu_checkout', payu_checkout, name="payu_checkout"),
    path('payu/failure', payu_failure, name="payu_failure"),
    path('payu/success', payu_success, name="payu_success"),

]
