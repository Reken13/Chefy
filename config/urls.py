from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('core.urls')),
    path('', include('core.dashboard_urls')),
    path('inventario/', include('inventory.urls')),
    path('recetas/', include('recipes.urls')),
    path('mise-en-place/', include('mise_en_place.urls')),
    path('compras/', include('purchasing.urls')),
    path('equipos/', include('equipment.urls')),
    path('produccion/', include('production.urls')),
    path('desperdicios/', include('waste.urls')),
    path('notificaciones/', include('notifications.urls')),
    # API endpoints
    path('api/', include('core.api_urls')),
    path('api/inventario/', include('inventory.api_urls')),
    path('api/recetas/', include('recipes.api_urls')),
    path('api/mise-en-place/', include('mise_en_place.api_urls')),
    path('api/compras/', include('purchasing.api_urls')),
    path('api/equipos/', include('equipment.api_urls')),
    path('api/produccion/', include('production.api_urls')),
    path('api/desperdicios/', include('waste.api_urls')),
    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
