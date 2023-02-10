from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from rest_framework.generics import RetrieveAPIView, CreateAPIView

from main.models import Bb, Rubric
from .serializers import BbSerializer, BbDetailSerializer, RubricSerializer


@api_view(['GET', 'POST'])
# @permission_classes((IsAuthenticatedOrReadOnly,))
def bbs(request):
    if request.method == 'GET':
        bbs = Bb.objects.filter(is_active=True) [:10]
        serializer = BbSerializer(bbs, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = BbDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @permission_classes((IsAuthenticatedOrReadOnly,))
def rubrics(request):
    if request.method == 'GET':
        rubric = Rubric.objects.filter(super_rubric__isnull=False)
        serializer = RubricSerializer(rubric, many=True)
        return Response(serializer.data)
    # if request.method == 'POST':
    #     serializer = RubricSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def bb_detail(request, pk):
    bb = Bb.objects.get(pk=pk)
    if request.method == 'GET':
        serializer = BbDetailSerializer(bb)
        return Response(serializer.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = BbDetailSerializer(bb, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        bb.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class BbDetailView(RetrieveAPIView):
#     queryset = Bb.objects.filter(is_active=True)
#     serializer_class = BbDetailSerialzer

