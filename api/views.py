from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.models import User
from core.models import (
    Categorie, SousCategorie, Annonce,
    GaleriePhoto, Horaire, Payment
)
from core.serializers.annonce import (
    AnnonceListSerializer,
    AnnonceSerializer,
    CategorieSerializer,
    PaymentSerializer
)
from .serializers.auth import (
    UserSerializer,
    LoginSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    AnnonceurRegisterSerializer
)
from users.serializers import UserProfileSerializer
from django.core.exceptions import ValidationError
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        logger.info(f"Login attempt received for email: {request.data.get('email', 'not provided')}")
        
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Login validation failed: {serializer.errors}")
            return Response(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        logger.info(f"Checking if user exists with email: {email}")
        
        # Check if user exists and authenticate
        user = authenticate(request, email=email, password=password)
        if user is None:
            logger.warning(f"Authentication failed for email: {email}")
            return Response(
                {'error': 'Email ou mot de passe incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            logger.warning(f"Inactive user attempted to login: {email}")
            return Response(
                {'error': 'Ce compte est inactif'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'profile_image': user.profile_image.url if user.profile_image else None
            }
        })
        
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Une erreur inattendue est survenue'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_annonceur_view(request):
    serializer = AnnonceurRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategorieList(generics.ListAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AnnonceList(generics.ListCreateAPIView):
    serializer_class = AnnonceListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Annonce.objects.filter(est_actif=True)
        
        # Récupérer les paramètres de filtrage
        category_id = self.request.query_params.get('categorie')
        subcategory_id = self.request.query_params.get('sous_categorie')
        search_query = self.request.query_params.get('search')

        # Filtrer par catégorie
        if category_id:
            queryset = queryset.filter(categorie_id=category_id)
        
        # Filtrer par sous-catégorie
        if subcategory_id:
            queryset = queryset.filter(sous_categorie_id=subcategory_id)

        # Recherche textuelle
        if search_query:
            queryset = queryset.filter(
                Q(titre__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(localisation__icontains=search_query)
            )

        return queryset.select_related(
            'categorie', 
            'sous_categorie'
        ).prefetch_related(
            'photos',
            'horaire_set'
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

class AnnonceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Annonce.objects.select_related(
            'categorie',
            'sous_categorie'
        ).prefetch_related(
            'photos',
            'horaire_set'
        )

    def perform_update(self, serializer):
        serializer.save(utilisateur=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    try:
        data = {
            'annonce': request.data.get('annonce'),
            'amount': request.data.get('amount'),
            'payment_type': request.data.get('payment_type'),
            'tarif': request.data.get('tarif'),
        }
        
        serializer = PaymentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            payment = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Payment validation errors: {serializer.errors}")
        return Response(
            {'error': serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    payments = Payment.objects.filter(user=request.user)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)

class CategorieViewSet(ReadOnlyModelViewSet):
    permission_classes = []
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class AnnonceViewSet(ReadOnlyModelViewSet):
    permission_classes = []
    serializer_class = AnnonceSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = Annonce.objects.filter(est_actif=True)
        category_id = self.request.query_params.get('categorie', None)
        subcategory_id = self.request.query_params.get('sous_categorie', None)

        if category_id:
            queryset = queryset.filter(categorie_id=category_id)
        if subcategory_id:
            queryset = queryset.filter(sous_categorie_id=subcategory_id)

        return queryset.select_related('categorie', 'sous_categorie').prefetch_related('photos')

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response([])

        queryset = self.get_queryset().filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class CinetPayWebhookView(APIView):
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"CinetPay webhook received: {request.data}")

            transaction_id = request.data.get('cpm_trans_id')
            status = request.data.get('status')
            amount = request.data.get('amount')
            currency = request.data.get('currency')
            payment_method = request.data.get('payment_method')
            
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for transaction_id: {transaction_id}")
                return Response({"message": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

            if status == "ACCEPTED":
                payment.status = "completed"
                payment.transaction_data = {
                    "amount": amount,
                    "currency": currency,
                    "payment_method": payment_method,
                    "transaction_id": transaction_id
                }
                payment.save()
                logger.info(f"Payment {transaction_id} marked as completed")
            elif status == "REFUSED":
                payment.status = "failed"
                payment.save()
                logger.info(f"Payment {transaction_id} marked as failed")

            return Response({"message": "Notification processed"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing CinetPay webhook: {str(e)}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    email = request.data.get('email')
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_annonces(request):
    annonces = Annonce.objects.filter(utilisateur=request.user)
    serializer = AnnonceListSerializer(annonces, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_tickets(request):
    tickets = Payment.objects.filter(
        user=request.user,
        payment_type='ticket'
    ).select_related('annonce')
    serializer = PaymentSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_chills(request):
    chills = Payment.objects.filter(
        user=request.user,
        payment_type='table'
    ).select_related('annonce')
    serializer = PaymentSerializer(chills, many=True)
    return Response(serializer.data) 