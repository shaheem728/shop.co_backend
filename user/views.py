import stripe
import random
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.response import Response
from . import models
from . import serializers
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import  TokenObtainPairView
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from datetime import datetime 
stripe.api_key = settings.STRIPE_SECRET_KEY
class StripeCheckoutViews(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data = request.data
            total = data.get('total', 0)
            line_items = [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Order Total'},
                        'unit_amount': int(float(total) * 100),  # Convert total to cents
                    },
                    'quantity': 1,
                }
            ]
            # Create the Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.SITE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.SITE_URL}/cancel",
            )

            return Response({'checkout_session': checkout_session.url}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.data.get("refresh_token")  # Fetch the 'refresh' key
        if not refresh_token:
            return Response({'error': 'Refresh token missing!'}, status=400)
        try:
            refresh = RefreshToken(refresh_token)
            tokens = {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                }
            response_data ={
                "tokens":tokens,
            }   
            return Response(response_data, status=status.HTTP_200_OK)
        except (InvalidToken, TokenError):
            return Response({'error': 'Invalid or expired refresh token!'}, status=401)
          
class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializers
    queryset = models.User.objects.all()
    lookup_field = "id"
    def get_queryset(self):
        return models.User.objects.filter(is_staff=False, is_superuser=False)
class UserCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSerializers
    queryset = models.User.objects.all()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = serializers.UserLoginSerializers(data=request.data)      
       # Validate serializer
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                tokens = {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                }
             # Store or update tokens in the database
                user_token, created = models.UserToken.objects.update_or_create(
                    user=user,
                    defaults={
                        'access_token': tokens['access_token'],
                        'refresh_token': tokens['refresh_token'],
                    }
                )
                response_data = {
                    'tokens': tokens,
                    'user_id': user.id,
                    'error': None,
                    'is_admin': user.is_staff,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials!'}, status=status.HTTP_400_BAD_REQUEST)
        except models.Profile.DoesNotExist:
            return Response({'error': 'Invalid mobile number!'}, status=status.HTTP_400_BAD_REQUEST)            
class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # Extract the refresh token from the request
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)            
class UserUpdateView(APIView):
    serializer_class = serializers.UserDetailSerializers
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        # Check if the authenticated user is trying to update their own details
        if request.user.id != id and not request.user.is_staff:
            raise PermissionDenied("You can only update your own details.")

        try:
            user = User.objects.get(id=id)  # Retrieve the user by ID
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update the user details
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
class mobileValidateView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = serializers.UserMobileSerializers(data=request.data)
        if serializer.is_valid():
            try:
                profile = models.Profile.objects.get(mobile=serializer.validated_data['mobile'])
                return Response({'message': 'Mobile number is valid.'})
            except models.Profile.DoesNotExist:
                return Response({'error': 'Invalid mobile!!'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class OTPValidateView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        otp = random.randint(1000, 9999)
        cache.set('otp', otp, timeout=300)  # Store OTP in cache for 5 minutes
        return Response({'otp': otp}, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = serializers.MobileOTPSerializers(data=request.data)
        if serializer.is_valid():
            stored_otp = cache.get('otp')  # Retrieve OTP from cache
            if stored_otp is None or serializer.validated_data['otp'] != str(stored_otp):
                return Response({'error': 'OTP not correct'}, status=status.HTTP_400_BAD_REQUEST)
            cache.delete('otp')  # Clear OTP after validation
            return Response({'message': 'OTP validated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ChangePasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = serializers.ChangePasswordSerializers(data=request.data)
        if serializer.is_valid():
            error = None
            profile = models.Profile.objects.get(mobile=serializer.validated_data['mobile'])
            user = profile.user
            if user:
                user.password = make_password(serializer.validated_data['password'])
                user.save()
            else:
                error = 'Profile not exists!!'  
            return Response({'error': error})  
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request, *args, **kwargs):
        serializer = serializers.OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Assign the logged-in user
            return Response(serializer.data, status=201)
class UserOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]  
    def get(self, request, user_id):
        try:
            # Retrieve all orders for the specified user ID
            user_orders = models.Order.objects.filter(user_id=user_id)
            serializer = serializers.orderDetailSerializer(user_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class OrderUpdateView(APIView):
    permission_classes = [AllowAny] 
    def put(self, request,uuid):
        try:
            order = models.Order.objects.get(uuid=uuid)
            order.isPaid = True
            order.paidAt = datetime.now()
            order.save()
            return Response({'message': 'Order updated successfully'}, status=status.HTTP_200_OK)
        except models.Order.DoesNotExist:
            return Response({'error': 'Order not exists!!'}, status=status.HTTP_404_NOT_FOUND)
            
