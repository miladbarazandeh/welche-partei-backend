from collections import Counter, defaultdict

from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Issue, Party, Position, QuizSession
from .serializers import IssueSerializer, PartySerializer, PositionSerializer

_DATA_CACHE_TTL      = 3600  # party/issue/position data is stable; cache 1 hour
_ANALYTICS_CACHE_TTL = 300   # 5 minutes


@api_view(["GET"])
def quiz_data(request):
    cached = cache.get("welchepartei:data")
    if cached is None:
        parties = PartySerializer(
            Party.objects.filter(is_active=True), many=True
        ).data
        issues = IssueSerializer(Issue.objects.all(), many=True).data
        positions = PositionSerializer(
            Position.objects.select_related("party", "issue").all(), many=True
        ).data
        cached = {"parties": parties, "issues": issues, "positions": positions}
        if parties:  # don't cache an empty dataset
            cache.set("welchepartei:data", cached, _DATA_CACHE_TTL)
    return Response(cached)


def _ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@api_view(["POST"])
def quiz_session(request):
    session_key = _ensure_session(request)
    data = request.data

    session, _ = QuizSession.objects.get_or_create(session_key=session_key)

    if "answers" in data:
        session.answers = data["answers"]
    if "weights" in data:
        session.weights = data["weights"]
    if "values_answers" in data:
        session.values_answers = data["values_answers"]
    if "pre_quiz_party" in data:
        session.pre_quiz_party = data["pre_quiz_party"] or ""
    if "post_quiz_party" in data:
        session.post_quiz_party = data["post_quiz_party"] or ""

    session.save()
    return Response({"ok": True})


@api_view(["GET"])
def analytics(request):
    cached = cache.get("welchepartei:analytics")
    if cached is not None:
        return Response(cached)

    sessions = list(QuizSession.objects.values("answers", "weights", "values_answers", "pre_quiz_party", "post_quiz_party"))
    total = len(sessions)

    # Per-issue answer distribution  {question_key: {0: n, 1: n, 2: n}}
    issue_answers = defaultdict(Counter)
    issue_weights = defaultdict(Counter)
    for s in sessions:
        for qk, slot in (s["answers"] or {}).items():
            if slot in (0, 1, 2):
                issue_answers[qk][slot] += 1
        for qk, w in (s["weights"] or {}).items():
            if w in (0, 1, 2, 3):
                issue_weights[qk][w] += 1

    # Values card distribution  {card_id: {a: n, b: n}}
    values_dist = defaultdict(Counter)
    for s in sessions:
        for card_id, choice in (s["values_answers"] or {}).items():
            if choice in ("a", "b"):
                values_dist[card_id][choice] += 1

    # Post-quiz vote intention  {party_id: count}
    post_vote: Counter = Counter()
    # Vote shift confusion matrix  {pre_party: {post_party: count}}
    vote_shift: dict[str, Counter] = defaultdict(Counter)
    for s in sessions:
        post = s.get("post_quiz_party") or ""
        pre  = s.get("pre_quiz_party") or ""
        if post:
            post_vote[post] += 1
        if pre and post:
            vote_shift[pre][post] += 1

    result = {
        "total_sessions": total,
        "issues": {
            qk: {
                "yes": issue_answers[qk].get(0, 0),
                "no": issue_answers[qk].get(1, 0),
                "neutral": issue_answers[qk].get(2, 0),
            }
            for qk in issue_answers
        },
        "weights": {
            qk: {
                "0": issue_weights[qk].get(0, 0),
                "1": issue_weights[qk].get(1, 0),
                "2": issue_weights[qk].get(2, 0),
                "3": issue_weights[qk].get(3, 0),
            }
            for qk in issue_weights
        },
        "values": {
            card_id: {
                "a": values_dist[card_id].get("a", 0),
                "b": values_dist[card_id].get("b", 0),
            }
            for card_id in values_dist
        },
        "post_vote": dict(post_vote),
        "vote_shift": {pre: dict(post_counts) for pre, post_counts in vote_shift.items()},
    }

    cache.set("welchepartei:analytics", result, _ANALYTICS_CACHE_TTL)
    return Response(result)


@api_view(["GET"])
def quiz_session_get(request):
    session_key = _ensure_session(request)
    try:
        session = QuizSession.objects.get(session_key=session_key)
        return Response({
            "answers": session.answers,
            "weights": session.weights,
            "values_answers": session.values_answers,
            "pre_quiz_party": session.pre_quiz_party,
            "post_quiz_party": session.post_quiz_party,
        })
    except QuizSession.DoesNotExist:
        return Response({"answers": {}, "weights": {}, "values_answers": {}, "pre_quiz_party": "", "post_quiz_party": ""})
