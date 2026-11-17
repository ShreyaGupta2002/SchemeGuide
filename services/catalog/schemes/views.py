from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Scheme
from .serializers import SchemeListSerializer, SchemeDetailSerializer


class SchemeListView(APIView):
    def get(self, request):
        schemes = Scheme.objects.filter(versions__status='published').distinct()
        serializer = SchemeListSerializer(schemes, many=True)
        return Response(serializer.data)


class SchemeDetailView(APIView):
    def get(self, request, scheme_id):
        try:
            scheme = Scheme.objects.get(id=scheme_id)
        except Scheme.DoesNotExist:
            return Response({'error': 'Scheme not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SchemeDetailSerializer(scheme)
        return Response(serializer.data)
