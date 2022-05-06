from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework import status, filters
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Guest, Movie, Reservation, Post
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import generics, mixins, viewsets
from .serializers import GuestSerializer, MovieSerializer, ReservationSerializer, PostSerializer
from .permissions import IsAuthorOrReadOnly

# 1- Without REST and no model query FBV (Function Based View)
def no_rest_no_model(request):
    guests = [
        {
            "id": 1,
            "name": "Omar",
            "mobile": 798789
        },
        {
            "id": 2,
            "name": "Yassin",
            "mobile": 4649754
        },
    ]
    return JsonResponse(guests, safe=False)


# 2- model data default django without rest
def no_rest_from_model(request):
    data = Guest.objects.all()
    response = {
        "guests": list(data.values('name', 'mobile'))
    }
    return JsonResponse(response, safe=False)


# List == GET
# Create == POST
# pk query == GET
# Update == PUT
# Delete (destroy) == DELETE

# 3- Functional based views
# 3.1- List and Create == GET and POST
@api_view(['GET', 'POST'])
def FBV_List(request):
    # GET
    if request.method == 'GET':
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)
    # POST
    elif request.method == 'POST':
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 3.2- GET PUT DELETE class based views -- pk
@api_view(['GET', 'PUT', 'DELETE'])
def FBV_pk(request, pk):
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExists:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET
    if request.method == 'GET':
        serializer = GuestSerializer(guest)
        return Response(serializer.data)
    # PUT
    elif request.method == 'PUT':
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # DELETE
    elif request.method == 'DELETE':
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 4- CBV Class Based View
# 4.1- List and Create == GET and POST
class CBV_List(APIView):
    def get(self, request):
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 4.2- GET PUT DELETE class based views -- pk
class CBV_pk(APIView):
    def get_object(self, pk):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExists:
            raise Http404

    def get(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest)
        return Response(serializer.data)

    def put(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        guest = self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 5 Mixins
# 5.1 List and Create == GET and POST
class Mixins_List(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)

# 5.2 GET PUT DELETE class based views -- pk
class Mixins_pk(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request, pk):
        return self.retrieve(request)

    def put(self, request, pk):
        return self.update(request)

    def delete(self, request, pk):
        return self.destroy(request)


# 6 Generics
# 6.1 List and Create == GET and POST
class Generics_List(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

# 6.2 GET PUT DELETE class based views -- pk
class Generics_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


# 7 ViewSets
class ViewSetsGuest(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class ViewSetsMovie(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['movie']

class ViewSetsReservation(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


# 8 Find Movie
@api_view(['GET'])
def find_movie(request):
    movies = Movie.objects.filter(
        movie=request.data['movie'],
        hall=request.data['hall']
    )
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

# 9 Create new reservation
@api_view(['POST'])
def new_reservation(request):
    movie = Movie.objects.get(
        movie=request.data['movie'],
        hall=request.data['hall']
    )
    guest = Guest()
    guest.name = request.data['name']
    guest.mobile = request.data['mobile']
    guest.save()

    reservation = Reservation()
    reservation.guest = guest
    reservation.movie = movie
    reservation.save()
    return Response(status=status.HTTP_201_CREATED)

# 10 Post author editor
class Post_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]