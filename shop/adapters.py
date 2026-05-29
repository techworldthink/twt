from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        if request.user.is_staff:
            return reverse('shop:admin_dashboard')
        return super().get_login_redirect_url(request)
