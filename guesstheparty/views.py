import random
from collections import defaultdict

from coolname import generate_slug

from django.core.cache import cache
from django.db.models import Count, Max, OuterRef, Q, Subquery
from rest_framework.decorators import api_view
from rest_framework.response import Response

_PROFANITY_BLOCKLIST = {
    "nigger",
    "nigga",
    "faggot",
    "kike",
    "spic",
    "chink",
    "cunt",
    "tranny",
}


def _generate_random_name():
    slug = generate_slug(2)  # e.g. "agile-tiger"
    name = "".join(part.capitalize() for part in slug.split("-"))
    number = random.randint(1000, 9999)
    return f"{name}:{number}"


from .game_config import (
    build_game_party_annotation,
    country_list,
    get_country_config,
    get_game_party,
    get_source_parties,
)
from .models import Answer, Politician, UserSession
from .serializers import AnswerSerializer, PoliticianSerializer


def _ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _country_config_or_404(country):
    config = get_country_config(country)
    if config is None:
        return Response({"error": "Country not found"}, status=404)
    return config


def _get_country_session(session_key, country_code):
    session, created = UserSession.objects.get_or_create(
        session_key=session_key,
        country=country_code,
    )
    if created and not session.name:
        existing_name = (
            UserSession.objects.filter(session_key=session_key)
            .exclude(pk=session.pk)
            .values_list("name", flat=True)
            .first()
        )
        session.name = existing_name or _generate_random_name()
        session.save(update_fields=["name", "updated_at"])
    return session, created


def _session_answers(session_key, country_code):
    return Answer.objects.filter(
        session_key=session_key, politician__country=country_code
    )


def _compute_streak(session_key, country_code):
    answers = _session_answers(session_key, country_code).order_by("-created_at")
    streak = 0
    for answer in answers.iterator():
        if answer.is_correct:
            streak += 1
        else:
            break
    return streak


def _session_stats(session_key, config):
    qs = _session_answers(session_key, config["code"])
    total = qs.count()
    score = qs.filter(is_correct=True).count()
    streak = _compute_streak(session_key, config["code"])
    try:
        user_session = UserSession.objects.get(
            session_key=session_key, country=config["code"]
        )
        best = user_session.best_streak
        name = user_session.name
    except UserSession.DoesNotExist:
        best = 0
        name = ""

    if config["supports_spectrum"]:
        spectrum_correct = qs.filter(is_spectrum_correct=True).count()
        spectrum_accuracy = round(spectrum_correct / total * 100, 1) if total else 0.0
    else:
        spectrum_correct = None
        spectrum_accuracy = None

    return {
        "name": name,
        "score": score,
        "streak": streak,
        "best": best,
        "total_answers": total,
        "spectrum_correct": spectrum_correct,
        "spectrum_accuracy": spectrum_accuracy,
    }


def _image_url_for(request, politician):
    if politician.image_local:
        return request.build_absolute_uri(f"/media/{politician.image_local}")
    return politician.thumbnail_url or politician.image_url or None


def _country_politicians(config):
    return Politician.objects.filter(
        country=config["code"],
        party__in=get_source_parties(config),
    ).exclude(Q(image_local="") & Q(thumbnail_url="") & Q(image_url=""))


def _actual_party_annotation(config):
    return build_game_party_annotation(config, "politician__party")


@api_view(["GET"])
def countries(request):
    return Response(
        [
            {
                "slug": config["slug"],
                "code": config["code"],
                "display_name": config["display_name"],
                "native_name": config["native_name"],
                "parties": config["game_parties"],
                "supports_spectrum": config["supports_spectrum"],
            }
            for config in country_list()
        ]
    )


@api_view(["GET"])
def country_config(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config
    return Response(
        {
            "slug": config["slug"],
            "code": config["code"],
            "display_name": config["display_name"],
            "native_name": config["native_name"],
            "parties": config["game_parties"],
            "supports_spectrum": config["supports_spectrum"],
        }
    )


@api_view(["GET"])
def session_stats(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config
    session_key = _ensure_session(request)
    return Response(_session_stats(session_key, config))


@api_view(["GET"])
def random_politician(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config

    session_key = _ensure_session(request)
    seen_ids = list(
        _session_answers(session_key, config["code"]).values_list(
            "politician_id", flat=True
        )
    )
    qs = _country_politicians(config).exclude(id__in=seen_ids)
    if not qs.exists():
        return Response({"game_over": True, **_session_stats(session_key, config)})

    politician = qs.order_by("?").first()
    user_session, _ = _get_country_session(session_key, config["code"])
    user_session.pending_politician_id = politician.id
    user_session.save(update_fields=["pending_politician_id", "updated_at"])

    serializer = PoliticianSerializer(politician, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
def submit_answer(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config

    politician_id = request.data.get("politician_id")
    guessed_party = request.data.get("guessed_party")
    if not politician_id or not guessed_party:
        return Response(
            {"error": "politician_id and guessed_party are required"}, status=400
        )
    if guessed_party not in config["game_parties"]:
        return Response({"error": "Invalid guessed_party"}, status=400)

    try:
        politician = Politician.objects.get(
            pk=politician_id,
            country=config["code"],
            party__in=get_source_parties(config),
        )
    except Politician.DoesNotExist:
        return Response({"error": "Politician not found"}, status=404)

    session_key = _ensure_session(request)
    user_session, _ = _get_country_session(session_key, config["code"])
    if user_session.pending_politician_id != int(politician_id):
        return Response(
            {"error": "politician_id does not match the current question"}, status=400
        )

    correct_party = get_game_party(config, politician.party)
    if correct_party is None:
        return Response({"error": "Politician not found"}, status=404)

    is_correct = correct_party == guessed_party
    if config["supports_spectrum"]:
        leaning_map = config["leaning_map"]
        is_spectrum_correct = (
            leaning_map.get(correct_party) == leaning_map.get(guessed_party)
            and leaning_map.get(guessed_party) is not None
        )
    else:
        is_spectrum_correct = None

    Answer.objects.create(
        politician=politician,
        session_key=session_key,
        guessed_party=guessed_party,
        is_correct=is_correct,
        is_spectrum_correct=is_spectrum_correct,
    )

    user_session.pending_politician_id = None
    if is_correct:
        streak = _compute_streak(session_key, config["code"])
        if streak > user_session.best_streak:
            user_session.best_streak = streak
    user_session.save(
        update_fields=["pending_politician_id", "best_streak", "updated_at"]
    )

    stats = _session_stats(session_key, config)
    return Response(
        {
            "correct": is_correct,
            "spectrum_correct": is_spectrum_correct,
            "correct_party": correct_party,
            "politician_name": politician.name,
            **stats,
        }
    )


@api_view(["GET"])
def stats(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config

    session_key = _ensure_session(request)
    answers = _session_answers(session_key, config["code"]).select_related("politician")
    recent = AnswerSerializer(answers[:20], many=True).data
    return Response({**_session_stats(session_key, config), "recent": recent})


@api_view(["GET"])
def parties(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config
    return Response(config["game_parties"])


@api_view(["GET"])
def politician_search(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config

    query = request.query_params.get("q", "").strip()
    if not query:
        return Response([])

    politicians = (
        Politician.objects.filter(
            country=config["code"],
            party__in=get_source_parties(config),
            name__icontains=query,
        )
        .exclude(Q(image_local="") & Q(thumbnail_url="") & Q(image_url=""))
        .order_by("name")[:20]
    )

    return Response(
        [
            {
                "reference": politician.reference,
                "name": politician.name,
                "party": get_game_party(config, politician.party),
                "full_party": politician.party,
                "parliament": politician.parliament,
                "image": _image_url_for(request, politician),
            }
            for politician in politicians
        ]
    )


@api_view(["GET"])
def politician_stats(request, country, reference):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config

    try:
        politician = Politician.objects.get(
            country=config["code"],
            reference=reference,
            party__in=get_source_parties(config),
        )
    except Politician.DoesNotExist:
        return Response({"error": "Politician not found"}, status=404)

    answers = Answer.objects.filter(politician=politician)
    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    guess_counts = {
        row["guessed_party"]: row["count"]
        for row in answers.values("guessed_party").annotate(count=Count("id"))
    }
    confusion = [
        {
            "party": party,
            "count": guess_counts.get(party, 0),
            "percentage": (
                round(guess_counts.get(party, 0) / total * 100, 1) if total else 0.0
            ),
        }
        for party in config["game_parties"]
    ]

    return Response(
        {
            "reference": politician.reference,
            "name": politician.name,
            "party": get_game_party(config, politician.party),
            "full_party": politician.party,
            "parliament": politician.parliament,
            "image": _image_url_for(request, politician),
            "image_page_url": politician.image_page_url,
            "license_short_name": politician.license_short_name,
            "license_url": politician.license_url,
            "author_name": politician.author_name,
            "author_url": politician.author_url,
            "credit_text": politician.credit_text,
            "credit_url": politician.credit_url,
            "total_answers": total,
            "accuracy": round(correct / total * 100, 1) if total else 0.0,
            "confusion": confusion,
        }
    )


_FAST_TTL = 93
_SLOW_TTL = 650
_LEADERBOARD_TTL = 307


def _get_leaderboard_snapshot(config):
    cache_key = f"leaderboard:{config['code']}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    session_name_sq = UserSession.objects.filter(
        session_key=OuterRef("session_key"),
        country=config["code"],
    ).values("name")[:1]

    sessions = list(
        Answer.objects.filter(
            politician__country=config["code"],
            politician__party__in=get_source_parties(config),
        )
        .values("session_key")
        .annotate(
            correct=Count("id", filter=Q(is_correct=True)),
            total=Count("id"),
            name=Subquery(session_name_sq),
        )
        .filter(total__gt=10)
        .order_by("-correct")
    )
    cache.set(cache_key, sessions, _LEADERBOARD_TTL)
    return sessions


def _top_users(sessions, session_key):
    return [
        {
            "name": row["name"] or "",
            "correct": row["correct"],
            "total": row["total"],
            "accuracy": (
                round(row["correct"] / row["total"] * 100, 1) if row["total"] else 0.0
            ),
            "is_current_user": row["session_key"] == session_key,
        }
        for row in sessions[:10]
    ]


_CACHE_MISS = object()


def _get_user_rank(config, session_key):
    cache_key = f"user_rank:{config['code']}:{session_key}"
    cached = cache.get(cache_key, _CACHE_MISS)
    if cached is not _CACHE_MISS:
        return cached

    base_qs = Answer.objects.filter(
        politician__country=config["code"],
        politician__party__in=get_source_parties(config),
    )

    user_stats = base_qs.filter(session_key=session_key).aggregate(
        correct=Count("id", filter=Q(is_correct=True)), total=Count("id")
    )

    correct = user_stats["correct"]
    total = user_stats["total"]

    rank = (
        base_qs.values("session_key")
        .annotate(correct=Count("id", filter=Q(is_correct=True)), total=Count("id"))
        .filter(correct__gt=correct)
        .count()
        + 1
    )

    result = {
        "rank": rank,
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total * 100, 1) if total else 0.0,
        "is_current_user": True,
    }

    cache.set(cache_key, result, _LEADERBOARD_TTL)
    return result


def _cached(key, ttl, compute):
    value = cache.get(key, _CACHE_MISS)
    if value is _CACHE_MISS:
        value = compute()
        cache.set(key, value, ttl)
    return value


def _source_answers(config):
    return Answer.objects.filter(
        politician__country=config["code"],
        politician__party__in=get_source_parties(config),
    )


def _pct(part, whole):
    return round(part / whole * 100, 1) if whole else 0.0


def _compute_fast_stats(config):
    answers = _source_answers(config)
    total_answers = answers.count()
    total_correct = answers.filter(is_correct=True).count()
    unique_players = answers.values("session_key").distinct().count()

    if config["supports_spectrum"]:
        total_spectrum_correct = answers.filter(is_spectrum_correct=True).count()
        spectrum_accuracy = _pct(total_spectrum_correct, total_answers)
    else:
        total_spectrum_correct = None
        spectrum_accuracy = None

    return {
        "total_answers": total_answers,
        "total_correct": total_correct,
        "overall_accuracy": _pct(total_correct, total_answers),
        "unique_players": unique_players,
        "total_spectrum_correct": total_spectrum_correct,
        "spectrum_accuracy": spectrum_accuracy,
    }


def _compute_best_streak(config):
    return (
        UserSession.objects.filter(country=config["code"]).aggregate(
            best=Max("best_streak")
        )["best"]
        or 0
    )


def _compute_pair_counts(config):
    """One group-by over (actual, guessed) that feeds parties, leanings,
    confusion and the confusion matrix."""
    return list(
        _source_answers(config)
        .annotate(actual_party=_actual_party_annotation(config))
        .values("actual_party", "guessed_party")
        .annotate(
            count=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
            spectrum_correct=Count("id", filter=Q(is_spectrum_correct=True)),
        )
        .exclude(actual_party="")
    )


def _get_pair_counts(config):
    return _cached(
        f"global_stats_pairs:{config['code']}",
        _SLOW_TTL,
        lambda: _compute_pair_counts(config),
    )


def _compute_politician_rows(config):
    return list(
        _source_answers(config)
        .annotate(actual_party=_actual_party_annotation(config))
        .values(
            "politician__reference",
            "politician__name",
            "actual_party",
            "politician__image_local",
            "politician__thumbnail_url",
            "politician__image_url",
        )
        .annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        )
        .exclude(actual_party="")
        .filter(total__gt=10)
    )


def _section_overview(config, request):
    return {
        **_cached(
            f"global_stats_fast:{config['code']}",
            _FAST_TTL,
            lambda: _compute_fast_stats(config),
        ),
        "global_best_streak": _cached(
            f"global_stats_streak:{config['code']}",
            _SLOW_TTL,
            lambda: _compute_best_streak(config),
        ),
    }


def _section_parties(config, request):
    party_totals = defaultdict(lambda: {"total": 0, "correct": 0, "spectrum_correct": 0})
    for row in _get_pair_counts(config):
        totals = party_totals[row["actual_party"]]
        totals["total"] += row["count"]
        totals["correct"] += row["correct"]
        totals["spectrum_correct"] += row["spectrum_correct"]

    party_stats = [
        {
            "party": party,
            "total": totals["total"],
            "correct": totals["correct"],
            "accuracy": _pct(totals["correct"], totals["total"]),
        }
        for party, totals in sorted(party_totals.items())
    ]

    leaning_stats = []
    if config["supports_spectrum"]:
        leaning_buckets = {}
        for party, totals in party_totals.items():
            leaning = config["leaning_map"].get(party)
            if leaning is None:
                continue
            bucket = leaning_buckets.setdefault(
                leaning,
                {"leaning": leaning, "total": 0, "correct": 0, "spectrum_correct": 0},
            )
            bucket["total"] += totals["total"]
            bucket["correct"] += totals["correct"]
            bucket["spectrum_correct"] += totals["spectrum_correct"]
        leaning_stats = [
            {
                **bucket,
                "accuracy": _pct(bucket["correct"], bucket["total"]),
                "spectrum_accuracy": _pct(bucket["spectrum_correct"], bucket["total"]),
            }
            for bucket in leaning_buckets.values()
        ]

    return {"party_stats": party_stats, "leaning_stats": leaning_stats}


def _section_confusion(config, request):
    pair_counts = _get_pair_counts(config)

    wrong_pairs = sorted(
        (
            (row["count"] - row["correct"], row)
            for row in pair_counts
            if row["count"] - row["correct"] > 0
        ),
        key=lambda item: -item[0],
    )[:8]
    confusion = [
        {
            "actual": row["actual_party"],
            "guessed": row["guessed_party"],
            "count": wrong,
        }
        for wrong, row in wrong_pairs
    ]

    cm_counts = defaultdict(lambda: defaultdict(int))
    cm_totals = defaultdict(int)
    for row in pair_counts:
        cm_counts[row["actual_party"]][row["guessed_party"]] += row["count"]
        cm_totals[row["actual_party"]] += row["count"]

    confusion_matrix = [
        {
            "actual": actual,
            "total": cm_totals[actual],
            "guesses": {
                guessed: {
                    "count": cm_counts[actual].get(guessed, 0),
                    "pct": _pct(cm_counts[actual].get(guessed, 0), cm_totals[actual]),
                }
                for guessed in config["game_parties"]
            },
        }
        for actual in config["game_parties"]
    ]

    return {"confusion": confusion, "confusion_matrix": confusion_matrix}


def _section_politicians(config, request):
    politician_stats = _cached(
        f"global_stats_politicians:{config['code']}",
        _SLOW_TTL,
        lambda: _compute_politician_rows(config),
    )

    def _accuracy(row):
        return row["correct"] / row["total"]

    def _image_url(row):
        if row["politician__image_local"]:
            return request.build_absolute_uri(
                f"/media/{row['politician__image_local']}"
            )
        return row["politician__thumbnail_url"] or row["politician__image_url"] or None

    def _serialize_politician(row):
        return {
            "reference": row["politician__reference"],
            "name": row["politician__name"],
            "party": row["actual_party"],
            "image": _image_url(row),
            "accuracy": round(_accuracy(row) * 100, 1),
        }

    def _sort_key(row):
        return (_accuracy(row), row["total"])

    return {
        "top_correct": [
            _serialize_politician(row)
            for row in sorted(politician_stats, key=_sort_key, reverse=True)[:10]
        ],
        "top_wrong": [
            _serialize_politician(row)
            for row in sorted(politician_stats, key=_sort_key)[:10]
        ],
    }


def _section_leaderboard(config, request):
    leaderboard_sessions = _get_leaderboard_snapshot(config)
    session_key = _ensure_session(request)
    return {
        "top_users": _top_users(leaderboard_sessions, session_key),
        "user_rank": _get_user_rank(config, session_key),
    }


_STATS_SECTIONS = {
    "overview": _section_overview,
    "parties": _section_parties,
    "confusion": _section_confusion,
    "politicians": _section_politicians,
    "leaderboard": _section_leaderboard,
}


@api_view(["GET"])
def global_stats_section(request, country, section):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config

    builder = _STATS_SECTIONS.get(section)
    if builder is None:
        return Response({"error": "Unknown stats section"}, status=404)

    return Response(builder(config, request))


@api_view(["GET"])
def global_stats(request, country):
    config = _country_config_or_404(country)
    if isinstance(config, Response):
        return config

    payload = {}
    for builder in _STATS_SECTIONS.values():
        payload.update(builder(config, request))
    return Response(payload)


@api_view(["PATCH"])
def session_name(request):
    raw = request.data.get("name", "")
    name = raw.strip() if isinstance(raw, str) else ""
    if not name:
        return Response({"error": "name is required"}, status=400)
    if len(name) > 50:
        return Response({"error": "name must be 50 characters or fewer"}, status=400)
    if any(slur in name.lower() for slur in _PROFANITY_BLOCKLIST):
        return Response({"error": "name contains disallowed content"}, status=400)
    session_key = _ensure_session(request)
    UserSession.objects.filter(session_key=session_key).update(name=name)
    return Response({"name": name})
