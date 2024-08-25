import json
import uuid
from django.http import JsonResponse
import pika
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from django.core.files.storage import default_storage
import csv
from .models import *
from .serializers import *
from .filters import CompanyFilter

from rest_framework.pagination import PageNumberPagination


class WelcomeView(APIView):
    def get(self, request):
        return Response("Companies Info")


class RegisterView(APIView):
    def get(self, request):
        try:
            queryset = User.objects.all()
            serializer_class = UserSerializer(queryset, many=True)
            return Response(serializer_class.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'  # Allow client to change the page size using this query parameter
    max_page_size = 100  # Maximum limit for page size


class CompanyFilterView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract the filter parameters from the request data
        filter_params = request.data
        print(filter_params)

        # Clean filter parameters (remove empty values)
        filter_params = {key: value for key, value in filter_params.items() if value}


        # Initialize the filter set with the extracted parameters
        filterset = CompanyFilter(filter_params, queryset=Company.objects.all())

        if filterset.is_valid():
            queryset = filterset.qs  # Filtered queryset

            # Instantiate the paginator and paginate the queryset
            # paginator = PageNumberPagination()
            # paginator.page_size = 10  # Set the number of items per page
            # paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            # # Serialize the paginated data
            # serializer = CompanySerializer(paginated_queryset, many=True)
            
            # # Get paginated response
            # paginated_response = paginator.get_paginated_response(serializer.data)

            # Add the count and any additional data to the paginated response
            # paginated_response.data['count'] = queryset.count()

            # Return the enhanced paginated response
            # return paginated_response
            response_data = {"count" : queryset.count()}
            return Response (response_data)
        else:
            print(filterset.errors)
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        
class SelectionDataView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch data for each type
        countries = Country.objects.all()
        states = State.objects.all()
        city = City.objects.all()
        years_founded = YearFounded.objects.all()
        industries = Industry.objects.all()

        # Serialize the data
        country_serializer = CountrySerializer(countries, many=True)
        state_serializer = StateSerializer(states, many=True)
        city_serializer = CitySerializer(states, many=True)
        year_founded_serializer = YearFoundedSerializer(years_founded, many=True)
        industry_serializer = IndustrySerializer(industries, many=True)

        # Combine all data into one response
        data = {
            'countries': country_serializer.data,
            'states': state_serializer.data,
            'years_founded': year_founded_serializer.data,
            'city' : city_serializer.data,
            'industries': industry_serializer.data
        }
        
        return Response(data)
 

def enqueue_task(file_path, chunk_size=5000):
    """Reads the CSV file in chunks and enqueues each chunk as a task to RabbitMQ."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='file_processing', durable=True)
        
        task_id = str(uuid.uuid4())  # Generate a unique task ID for tracking

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            chunk = []
            for index, row in enumerate(reader):
                
                chunk.append(row)
                if (index + 1) % chunk_size == 0:
                    task_data = {
                        'task_id': task_id,
                        'chunk': chunk,
                    }
                    channel.basic_publish(
                        exchange='',
                        routing_key='file_processing',
                        body=json.dumps(task_data),
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # Make message persistent
                        )
                    )
                    chunk = []  # Reset chunk
            # Publish the last chunk if it exists
            if chunk:
                task_data = {
                    'task_id': task_id,
                    'chunk': chunk,
                }
                channel.basic_publish(
                    exchange='',
                    routing_key='file_processing',
                    body=json.dumps(task_data),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                    )
                )
    except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
        print(f"Connection to RabbitMQ lost during enqueue, retrying... Error: {e}")
        # Optional: implement a retry mechanism here
    except Exception as e:
        print(f"Error enqueueing task: {e}")
    finally:
        connection.close()

class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        """Handles the file upload and enqueues it for processing."""
        try:
            file_obj = request.data['file']
            file_name = default_storage.save(file_obj.name, file_obj)
            file_path = default_storage.path(file_name)

            # Enqueue the CSV processing task in chunks
            enqueue_task(file_path)

            return JsonResponse({"success": True, "message": "File uploaded successfully and processing started."}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(str(e))
            return JsonResponse({"success": False, "message": "Error occurred while uploading file"}, status=status.HTTP_400_BAD_REQUEST)