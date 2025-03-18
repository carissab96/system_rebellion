from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContextViewSet,
    PatternValidatorView,
    PatternAnalyzerView,
    PatternMatcherView,
    AdvancedPatternDetectorView,
    PatternLearnerView,
    ContextManagerView
);

router = DefaultRouter()
router.register(r'context', ContextViewSet, basename='context')

urlpatterns = [
    path('', include(router.urls)),
    path('validate/', PatternValidatorView.as_view({
        'post': 'create'
    }), name='pattern-validate'),
    path('analyze/', PatternAnalyzerView.as_view({
        'post': 'create'
    }), name='pattern-analyze'),
    path('match/', PatternMatcherView.as_view({
        'post': 'create'
    }), name='pattern-match'),
    path('advanced-detect/', AdvancedPatternDetectorView.as_view({
        'post': 'create'
    }), name='advanced-pattern-detect'),
    path('context-manage/', ContextManagerView.as_view({
        'post': 'create'
    }), name='context-manager'),
    path('learn/', PatternLearnerView.as_view({
        'post': 'create'
    }), name='pattern-learn'),
]