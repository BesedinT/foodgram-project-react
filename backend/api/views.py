from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (CustomUserSerializer, FollowSerializer,
                          IngredientSerializer, RecipeReadOnlySerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          TagSerializer)

from recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        obj = Favorite.objects.filter(user=request.user, recipe__id=pk)
        if request.method == 'POST':
            if obj.exists():
                return Response({'Рецепт уже в избранном!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'Рецепта нет в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        obj = ShoppingCart.objects.filter(user=request.user, recipe__id=pk)
        if request.method == 'POST':
            if obj.filter(user=request.user,
                          recipe__id=pk).exists():
                return Response({'Рецепт уже в корзине!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'Рецепт уже удален!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response({'В корзине нет рецептов'},
                            status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
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
        followed = get_object_or_404(User, id=id)
        follower = request.user
        obj = Follow.objects.filter(author=followed, user=follower)

        if request.method == 'POST':
            if obj.exists():
                return Response({'Вы уже подписаны на пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.get_or_create(
                user=follower,
                author=followed
            )
            return Response(
                FollowSerializer(followed, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'Вы не подписаны на пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)

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
