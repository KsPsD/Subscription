from django.utils.deprecation import MiddlewareMixin


class ForceLoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        from django.contrib.auth.models import User

        user = User.objects.get(
            username="admin"
        )  # 여기서 'your_username'을 강제 로그인할 사용자의 이름으로 대체합니다.
        request.user = user
