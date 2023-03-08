from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          FollowAddSerializer, FollowSerializer,
                          IngredientSerializer, RecipeReadOnlySerializer,
                          RecipeWriteSerializer, ShoppingCartSerializer,
                          TagSerializer)

from recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        return self.add_to(request=request,
                           serializers=FavoriteSerializer, pk=pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_from(request=request,
                                model=Favorite, pk=pk)

    @action(detail=True, methods=['post'],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.add_to(request=request,
                           serializers=ShoppingCartSerializer, pk=pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_from(request=request,
                                model=ShoppingCart, pk=pk)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(amount=Sum('amount'))
        return self.shopping_file(user, ingredients)

    @staticmethod
    def add_to(request, serializers, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_from(request, model, pk):
        get_object_or_404(
            model,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def shopping_file(user, ingredients):
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            data = {'user': request.user.id, 'author': id}
            serializer = FollowAddSerializer(data=data,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            get_object_or_404(Follow, user=request.user,
                              author=get_object_or_404(User, id=id)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False
    )
    def me(self, request):
        if request.user.is_authenticated:
            return Response(CustomUserSerializer(
                request.user,
                context={'request': request}
            ).data, status=status.HTTP_200_OK)
        return Response({'Вы не авторизованы'},
                        status=status.HTTP_400_BAD_REQUEST)
