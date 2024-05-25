from django.shortcuts import render

from rest_framework_simplejwt.views import TokenObtainPairView
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        logger.info(f'Received token request: {request.data}')
        response = super().post(request, *args, **kwargs)
        logger.info(f'Token response status: {response.status_code}')
        logger.info(f'Token response data: {response.data}')
        return response

