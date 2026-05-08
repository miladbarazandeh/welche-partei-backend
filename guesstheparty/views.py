import random

from django.core.cache import cache
from django.db.models import Count, Max, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Answer, Politician, UserSession
from .serializers import AnswerSerializer, PoliticianSerializer

GAME_PARTIES = ['SPD', 'CDU/CSU', 'Grüne', 'AfD', 'Die Linke', 'FDP']


def _ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _compute_streak(session_key):
    answers = Answer.objects.filter(session_key=session_key).order_by('-created_at')
    streak = 0
    for a in answers.iterator():
        if a.is_correct:
            streak += 1
        else:
            break
    return streak


def _session_stats(session_key):
    score = Answer.objects.filter(session_key=session_key, is_correct=True).count()
    streak = _compute_streak(session_key)
    try:
        best = UserSession.objects.get(session_key=session_key).best_streak
    except UserSession.DoesNotExist:
        best = 0
    return {'score': score, 'streak': streak, 'best': best}


@api_view(['GET'])
def session_stats(request):
    session_key = _ensure_session(request)
    return Response(_session_stats(session_key))


@api_view(['GET'])
def random_politician(request):
    session_key = _ensure_session(request)

    seen_ids = list(
        Answer.objects.filter(session_key=session_key).values_list('politician_id', flat=True)
    )
    qs = Politician.objects.filter(party__in=GAME_PARTIES).exclude(id__in=seen_ids)
    if not qs.exists():
        qs = Politician.objects.filter(party__in=GAME_PARTIES)

    pk = random.choice(list(qs.values_list('id', flat=True)))
    politician = Politician.objects.get(pk=pk)
    serializer = PoliticianSerializer(politician, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
def submit_answer(request):
    politician_id = request.data.get('politician_id')
    guessed_party = request.data.get('guessed_party')

    if not politician_id or not guessed_party:
        return Response({'error': 'politician_id and guessed_party are required'}, status=400)

    try:
        politician = Politician.objects.get(pk=politician_id)
    except Politician.DoesNotExist:
        return Response({'error': 'Politician not found'}, status=404)

    session_key = _ensure_session(request)
    is_correct = politician.party == guessed_party

    Answer.objects.create(
        politician=politician,
        session_key=session_key,
        guessed_party=guessed_party,
        is_correct=is_correct,
    )

    # Update best streak if needed
    if is_correct:
        streak = _compute_streak(session_key)
        us, _ = UserSession.objects.get_or_create(session_key=session_key)
        if streak > us.best_streak:
            us.best_streak = streak
            us.save(update_fields=['best_streak', 'updated_at'])

    stats = _session_stats(session_key)

    return Response({
        'correct': is_correct,
        'correct_party': politician.party,
        'politician_name': politician.name,
        **stats,
    })


@api_view(['GET'])
def stats(request):
    session_key = _ensure_session(request)
    answers = Answer.objects.filter(session_key=session_key)
    recent = AnswerSerializer(answers[:20], many=True).data
    return Response({**_session_stats(session_key), 'recent': recent})


@api_view(['GET'])
def parties(request):
    return Response(GAME_PARTIES)


@api_view(['GET'])
def global_stats(request):
    cached = cache.get('global_stats')
    if cached is not None:
        return Response(cached)

    total_answers = Answer.objects.count()
    total_correct = Answer.objects.filter(is_correct=True).count()
    overall_accuracy = round(total_correct / total_answers * 100, 1) if total_answers else 0.0
    unique_players = Answer.objects.values('session_key').distinct().count()
    global_best_streak = UserSession.objects.aggregate(best=Max('best_streak'))['best'] or 0

    party_qs = (
        Answer.objects
        .values('politician__party')
        .annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True)),
        )
        .order_by('politician__party')
    )
    party_stats = [
        {
            'party': row['politician__party'],
            'total': row['total'],
            'correct': row['correct'],
            'accuracy': round(row['correct'] / row['total'] * 100, 1) if row['total'] else 0.0,
        }
        for row in party_qs
    ]

    confusion_qs = (
        Answer.objects
        .filter(is_correct=False)
        .values('politician__party', 'guessed_party')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )
    confusion = [
        {
            'actual': row['politician__party'],
            'guessed': row['guessed_party'],
            'count': row['count'],
        }
        for row in confusion_qs
    ]

    politician_stats = list(
        Answer.objects
        .values('politician__name', 'politician__party', 'politician__image_local')
        .annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True)),
        )
    )

    def accuracy(row):
        return row['correct'] / row['total']

    def image_url(row):
        img = row['politician__image_local']
        if not img:
            return None
        return request.build_absolute_uri(f'/media/{img}')

    def serialize_politician(row):
        return {
            'name': row['politician__name'],
            'party': row['politician__party'],
            'image': image_url(row),
            'accuracy': round(accuracy(row) * 100, 1),
        }

    top_correct = [serialize_politician(r) for r in sorted(politician_stats, key=accuracy, reverse=True)[:5]]
    top_wrong = [serialize_politician(r) for r in sorted(politician_stats, key=accuracy)[:5]]

    data = {
        'total_answers': total_answers,
        'total_correct': total_correct,
        'overall_accuracy': overall_accuracy,
        'unique_players': unique_players,
        'global_best_streak': global_best_streak,
        'party_stats': party_stats,
        'confusion': confusion,
        'top_correct': top_correct,
        'top_wrong': top_wrong,
    }
    cache.set('global_stats', data, 60)
    return Response(data)
