import base64

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .generator import BrochureCalculationError, generate_brochure_jpeg
from .serializers import BrochureRequestSerializer


class BrochureGenerateView(APIView):
    # Account-scoped output (matches the app gating this behind login) — not for guests.
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BrochureRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            jpeg_bytes = generate_brochure_jpeg(
                price=d["price"],
                down_payment=d["down_payment"],
                term_months=d["term_months"],
                annual_rate_percent=d["annual_rate_percent"],
            )
        except BrochureCalculationError as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response({"image_base64": base64.b64encode(jpeg_bytes).decode("ascii")})
