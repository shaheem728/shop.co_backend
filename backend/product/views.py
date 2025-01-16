from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Products,Review
from .serializers import ProductsSerializer,ProductReviewSerializer
from django.db.models import Q
from rest_framework.permissions import AllowAny,IsAuthenticated

class ProductListviews(ListAPIView):
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Get search query
        query = self.request.query_params.get('search', '')
        search_terms = query.split()  # Split the search query into individual words

        # Construct a dynamic Q object to filter for matching any word in name or description or category or style
        q_objects = Q()
        for term in search_terms:
            q_objects |= Q(name__icontains=term) | Q(description__icontains=term) | Q(category__name__icontains=term) | Q(style__name__icontains=term)
        # Filter products based on the Q object
        products = Products.objects.filter(q_objects)
        # Handle pagination
        page = self.request.query_params.get('page')
        paginator = Paginator(products, 9)  # Show 9 products per page
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        # Serialize data
        serializer = self.get_serializer(products, many=True)

        # Custom response with pagination data
        return Response({
            'products': serializer.data,
            'page': page,
            'pages': paginator.num_pages,
        }, status=status.HTTP_200_OK)        
class ReviewCreateView(CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]   
class ReviewListView(ListAPIView):
    serializer_class = ProductReviewSerializer
    queryset= Review.objects.all()
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(product__uuid=self.kwargs['uuid'])  
        return qs

    
   