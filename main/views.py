from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Course, Certificate, Event
from .serializers import CourseSerializer, CertificateSerializer, EventSerializer, ContactFormSerializer
import environ

env = environ.Env()
environ.Env.read_env()

class CertificateDetailView(generics.RetrieveAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class CertificateListView(generics.ListAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


def reset_database(request):
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")
    return HttpResponse("Database reset successfully.")


class ContactFormView(APIView):
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            # Формирование сообщения
            message = f"""
            New student registration:

            Student Name: {data['studentName']}
            Date of Birth: {data['dob']}
            Address: {data['address']}
            Primary Phone: {data['primaryPhone']}
            Secondary Phone: {data['secondaryPhone']}
            Parent Name: {data['parentName']}
            Email: {data['email']}
            Emergency Contact: {data['emergencyContact']}
            Minor Name: {data['minorName']}
            Minor Age: {data['minorAge']}
            Signature: {data['signature']}
            Date: {data['date']}
            Zelle: {data.get('Zelle', 'Not provided')}
            Policies Accepted: {all(data['policies'])}
            Waiver Accepted: {data['waiver']}
            """

            # Отправка email
            try:
                send_mail(
                    subject="New Student Registration",
                    message=message,
                    from_email=env('EMAIL_HOST_USER'),
                    recipient_list=["beglaryan4.arman@gmail.com"],
                )
                return Response({'message': 'Registration submitted successfully.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f'Email error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)