from drf_spectacular.views import SpectacularSwaggerView

class CustomSwaggerView(SpectacularSwaggerView):
    def get_template_context(self, *args, **kwargs):
        context = super().get_template_context(*args, **kwargs)
        context["SWAGGER_UI_SETTINGS"] = {
            "persistAuthorization": True,  # Keeps token after reload
            "dom_id": "#swagger-ui",
            "displayRequestDuration": True,
        }
        return context
