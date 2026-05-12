from django.db.models import Case, CharField, Value, When


DE_PARTY_MAP = {
    "SPD": "SPD",
    "CDU": "CDU/CSU",
    "CSU": "CDU/CSU",
    "CDU/CSU": "CDU/CSU",
    "BÜNDNIS 90/­DIE GRÜNEN": "Grüne",
    "BÜNDNIS 90/DIE GRÜNEN": "Grüne",
    "GRÜNE": "Grüne",
    "Grüne": "Grüne",
    "AfD": "AfD",
    "Die Linke": "Die Linke",
    "DIE LINKE": "Die Linke",
    "FDP": "FDP",
}

US_PARTY_MAP = {
    "Democratic": "Democratic",
    "Democratic-Farmer-Labor": "Democratic",
    "Democratic/Working Families": "Democratic",
    "Democratic/Progressive": "Democratic",
    "Democratic/Independence/Working Families": "Democratic",
    "Republican": "Republican",
    "Republican/Conservative": "Republican",
    "Republican/Conservative/Independence": "Republican",
    "Republican/Conservative/Independence/Reform": "Republican",
    "Independent": "Independent",
    "Nonpartisan": "Other",
}

COUNTRY_SETTINGS = {
    "de": {
        "slug": "de",
        "code": "DE",
        "display_name": "Germany",
        "native_name": "Deutschland",
        "game_parties": ["SPD", "CDU/CSU", "Grüne", "AfD", "Die Linke", "FDP"],
        "party_map": DE_PARTY_MAP,
        "supports_spectrum": True,
        "spectrum_label": "left_right",
        "leaning_map": {
            "SPD": "left",
            "Grüne": "left",
            "Die Linke": "left",
            "CDU/CSU": "right",
            "FDP": "right",
            "AfD": "right",
        },
    },
    "us": {
        "slug": "us",
        "code": "US",
        "display_name": "United States",
        "native_name": "United States",
        "game_parties": ["Democratic", "Republican", "Independent", "Other"],
        "party_map": US_PARTY_MAP,
        "supports_spectrum": False,
        "spectrum_label": None,
        "leaning_map": {},
    },
}


def get_country_config(country_slug_or_code):
    normalized = (country_slug_or_code or "").strip()
    if not normalized:
        return None

    config = COUNTRY_SETTINGS.get(normalized.lower())
    if config is not None:
        return config

    upper = normalized.upper()
    for candidate in COUNTRY_SETTINGS.values():
        if candidate["code"] == upper:
            return candidate
    return None


def get_game_party(country_or_config, raw_party):
    config = (
        country_or_config
        if isinstance(country_or_config, dict)
        else get_country_config(country_or_config)
    )
    if config is None:
        return None
    return config["party_map"].get((raw_party or "").strip())


def get_source_parties(country_or_config):
    config = (
        country_or_config
        if isinstance(country_or_config, dict)
        else get_country_config(country_or_config)
    )
    if config is None:
        return ()
    return tuple(config["party_map"].keys())


def build_game_party_annotation(country_or_config, field_name="party"):
    config = (
        country_or_config
        if isinstance(country_or_config, dict)
        else get_country_config(country_or_config)
    )
    if config is None:
        return Value("", output_field=CharField())

    return Case(
        *[
            When(**{field_name: raw_party}, then=Value(game_party))
            for raw_party, game_party in config["party_map"].items()
        ],
        default=Value(""),
        output_field=CharField(),
    )


def country_list():
    return list(COUNTRY_SETTINGS.values())
