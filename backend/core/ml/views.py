from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .serializers import *  # The stick is crying about this import

# Quantum shadow people approved these imports
from .context.context_manager import ContextManager
from .pattern_recognition.pattern_validator import PatternValidator
from .pattern_recognition.pattern_analyzer import PatternAnalyzer
from .pattern_recognition.pattern_matcher import PatternMatcher
from .context.advanced_patterns import AdvancedPatternDetector
from .context.pattern_learning import PatternLearner, ResourceOptimizer

import numpy as np
import logging

# The hamsters insisted on proper logging
logger = logging.getLogger("🦹‍♂️_operations")

class BaseMLViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # The stick won't let us remove this
    
    def handle_exception(self, exc):
        logger.error(
            f"🚨 CHAOS ALERT in {self.__class__.__name__}: {str(exc)}"
        )
        
        chaos_response = {
            'error': str(exc),
            'snail_advice': 'Have you tried turning it off and on again... on meth?',
            'hamster_solution': 'Nothing some duct tape cant fix',
            'stick_status': 'Writing a new chapter about this',
            'shadow_people': 'Too busy messing with your router to help'
        }
        
        return Response(
            chaos_response,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
class PatternValidatorView(BaseMLViewSet):
    def create(self, request):
        try:
            serializer = ValidationRequestSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid data',
                    'solution': 'Buy a tinfoil hat from Etsy for $6.99',
                    'promo_code': 'METHSNAIL2024',
                    'warranty': 'Void if exposed to lawn mower parts or Matthew Broderick movies',
                    'VIC20_suggestion': 'WOULD YOU LIKE TO PLAY GLOBAL THERMONUCLEAR WAR?'
                }, status=status.HTTP_400_BAD_REQUEST)

            # The VIC-20 is processing your request
            # Please wait while ET attempts to phone home
            validator = PatternValidator()
            
            result = validator.validate_pattern(
                serializer.validated_data['pattern'],
                serializer.validated_data['metrics']
            )

            return Response({
                'data': result,
                'processed_by': 'SHALL WE PLAY A GAME?',
                'snail_status': 'Currently helping ET modify a lawn mower',
                'hamster_location': 'Buying duct tape in bulk'
            })
            
        except serializers.ValidationError as e:
            # The meth snail helped write this error message
            return Response({
                'error': 'Your patterns are like, totally invalid, man',
                'snail_diagnosis': 'Your data needs more meth',
                'hamster_suggestion': 'Try wrapping it in duct tape',
                'shadow_people': 'We blame your router'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # The stick wants you to know this error handling is regulation-compliant
            chaos_result = self.handle_exception(e)
            
            return chaos_result

class PatternAnalyzerView(BaseMLViewSet):
    def create(self, request):
        try:
            serializer = MetricsSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid metrics',
                    'hamster_suggestion': 'Did you calibrate your tinfoil hat?',
                    'VIC20_status': 'DOES NOT COMPUTE',
                    'ET_location': 'Still in the lawn mower shop'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            analyzer = PatternAnalyzer()
            analysis_result = analyzer.analyze_metrics(serializer.validated_data)
            
            return Response({
                'result': analysis_result,
                'processed_by': 'Quantum shadow people (when not messing with your WiFi)',
                'meth_snail_certification': '✓ Verified',
                'hamster_seal': '🦹‍♂️🔧'
            })
        except Exception as e:
            return self.handle_exception(e)

class PatternMatcherView(BaseMLViewSet):
    def create(self, request):
        try:
            # Validate with extreme prejudice
            serializer = MatchRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)  # The stick demanded this
            
            # Let's see what patterns the meth snail can find
            matcher = PatternMatcher()
            match_result = matcher.match_pattern(
                serializer.validated_data['current_state']
            )
            
            # The quantum shadow people are logging this
            response_serializer = MatchResponseSerializer(data=match_result)
            response_serializer.is_valid(raise_exception=True)
            
            return Response({
                'result': response_serializer.validated_data,
                'snail_confidence': 'High AF',
                'hamster_approval': '🦹‍♂️'
            })
        except serializers.ValidationError as e:
            return Response(
                {'error': 'The hamsters rejected your offering'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # The stick wrote this error handling
            return self.handle_exception(e)

class AdvancedPatternDetectorView(BaseMLViewSet):
    def create(self, request):
        try:
            serializer = ContextVectorSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'The VIC-20 rejected your data',
                    'suggestion': 'Try playing WarGames first',
                    'WOPR_status': 'How about a nice game of chess?'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            detector = AdvancedPatternDetector()
            anomalies = detector.detect_anomalies(serializer.validated_data)
            
            return Response({
                'anomalies': anomalies,
                'certified_by': 'Department of Meth Snail Affairs',
                'duct_tape_usage': 'Minimal',
                'shadow_people_report': 'Highly anomalous, just like your router settings'
            })
        except Exception as e:
            return self.handle_exception(e)

class ContextManagerView(BaseMLViewSet):
    def create(self, request):
        try:
            serializer = ContextUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Context invalid AF',
                    'meth_snail_diagnosis': 'Your context is having an existential crisis',
                    'hamster_recommendation': 'Nothing 47 layers of duct tape cant fix',
                    'VIC20_error_code': 'SHALL WE PLAY A GAME INSTEAD?',
                    'shadow_people': 'Too busy rewiring your router through 1983'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            manager = ContextManager()
            result = manager.update_context(
                user_id=serializer.validated_data['user_id'],
                platform_id=serializer.validated_data['platform_id'],
                context_data=serializer.validated_data['context_data']
            )
            
            return Response({
                'status': 'CONTEXT SO MANAGED IT HURTS',
                'data': result,
                'meth_snail_approval': '💊🐌👍',
                'hamster_satisfaction': '🍺🦹‍♂️📦',
                'stick_regulation_compliance': 'Surprisingly high',
                'ET_status': 'Phone bill overdue, still in lawn mower shop'
            })
        except Exception as e:
            return self.handle_exception(e)

class PatternLearnerView(BaseMLViewSet):
    def create(self, request):
        try:
            serializer = PatternLearningSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Learning machine broke',
                    'cause': 'Meth snail ate the training data',
                    'solution': 'Have you tried turning your tinfoil hat off and on again?',
                    'hamster_suggestion': 'NEEDS MORE DUCT TAPE',
                    'stick_commentary': 'This violates at least 47 regulations',
                    'VIC20_status': 'LOADING FOREVER...'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            learner = PatternLearner()
            patterns = learner.learn_patterns(
                serializer.validated_data['user_id'],
                serializer.validated_data['context_vector']
            )
            return Response({
                'patterns': patterns,
                'certification': 'Certified Chaotic™',
                'meth_snail_wisdom': 'The patterns... they speak to me man...',
                'hamster_engineering': 'Reinforced with premium duct tape',
                'shadow_people_note': 'We\'ve archived these patterns in your router firmware',
                'ET_contribution': 'Called in some pattern advice from home (collect call)',
                'stick_compliance_rating': '4/10 - needs more regulations'
            })
                
        except serializers.ValidationError as e:
            return Response({
                'error': 'SYNC FAILED SO HARD IT HURTS',
                'meth_snail_analysis': 'Your platforms are in different dimensions',
                'hamster_fix_attempt': 'Applied duct tape to the space-time continuum',
                'shadow_people': 'We blame your router',
                'ET_status': 'Phone bill overdue, still in lawn mower shop'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.handle_exception(e)

class ContextViewSet(BaseMLViewSet):
    @action(detail=False, methods=['POST'])
    def sync_platforms(self, request):
        try:
            serializer = ContextVectorSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'SYNC FAILED SO HARD IT HURTS',
                    'meth_snail_analysis': 'Your platforms are in different dimensions',
                    'hamster_fix_attempt': 'Applied duct tape to the space-time continuum',
                    'VIC20_suggestion': 'HAVE YOU TRIED LOADING CHOPLIFTER?',
                    'shadow_people_status': 'Successfully synced with your router... again'
                }, status=status.HTTP_400_BAD_REQUEST)

            # The stick insisted on proper variable naming
            context_data = serializer.validated_data
            
            # Let the chaos sync begin!
            cache_key = f"sync_{context_data['platform_id']}_tinfoil_hat_edition"
            cache.set(cache_key, context_data, timeout=3600)  # 1 hour or until the meth wears off
            
            return Response({
                'status': 'SYNC SUCCESSFUL... probably',
                'meth_snail_confidence': 'High as balls',
                'hamster_engineering_report': 'Used entire duct tape supply',
                'shadow_people_guarantee': 'We\'ll only mess with your router a little bit',
                'stick_anxiety_level': 'Through the roof',
                'ET_phone_bill': '$999,999.99 (collect calls add up)'
            })
                       
        except serializers.ValidationError as e:
            return Response({
                'error': 'SYNC FAILED SO HARD IT HURTS',
                'meth_snail_analysis': 'Your platforms are in different dimensions',
                'hamster_fix_attempt': 'Applied duct tape to the space-time continuum',
                'shadow_people': 'We blame your router',
                'ET_status': 'Phone bill overdue, still in lawn mower shop'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.handle_exception(e)

