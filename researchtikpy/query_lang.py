from dataclasses import field
from typing import List, Literal, Union
from pydantic import ConfigDict, RootModel
from pydantic.dataclasses import dataclass

VideoLength = Literal["SHORT", "MID", "LONG", "EXTRA_LONG"]
RegionCodes = Literal[
    "FR",
    "TH",
    "MM",
    "BD",
    "IT",
    "NP",
    "IQ",
    "BR",
    "US",
    "KW",
    "VN",
    "AR",
    "KZ",
    "GB",
    "UA",
    "TR",
    "ID",
    "PK",
    "NG",
    "KH",
    "PH",
    "EG",
    "QA",
    "MY",
    "ES",
    "JO",
    "MA",
    "SA",
    "TW",
    "AF",
    "EC",
    "MX",
    "BW",
    "JP",
    "LT",
    "TN",
    "RO",
    "LY",
    "IL",
    "DZ",
    "CG",
    "GH",
    "DE",
    "BJ",
    "SN",
    "SK",
    "BY",
    "NL",
    "LA",
    "BE",
    "DO",
    "TZ",
    "LK",
    "NI",
    "LB",
    "IE",
    "RS",
    "HU",
    "PT",
    "GP",
    "CM",
    "HN",
    "FI",
    "GA",
    "BN",
    "SG",
    "BO",
    "GM",
    "BG",
    "SD",
    "TT",
    "OM",
    "FO",
    "MZ",
    "ML",
    "UG",
    "RE",
    "PY",
    "GT",
    "CI",
    "SR",
    "AO",
    "AZ",
    "LR",
    "CD",
    "HR",
    "SV",
    "MV",
    "GY",
    "BH",
    "TG",
    "SL",
    "MK",
    "KE",
    "MT",
    "MG",
    "MR",
    "PA",
    "IS",
    "LU",
    "HT",
    "TM",
    "ZM",
    "CR",
    "NO",
    "AL",
    "ET",
    "GW",
    "AU",
    "KR",
    "UY",
    "JM",
    "DK",
    "AE",
    "MD",
    "SE",
    "MU",
    "SO",
    "CO",
    "AT",
    "GR",
    "UZ",
    "CL",
    "GE",
    "PL",
    "CA",
    "CZ",
    "ZA",
    "AI",
    "VE",
    "KG",
    "PE",
    "CH",
    "LV",
    "PR",
    "NZ",
    "TL",
    "BT",
    "MN",
    "FJ",
    "SZ",
    "VU",
    "BF",
    "TJ",
    "BA",
    "AM",
    "TD",
    "SI",
    "CY",
    "MW",
    "EE",
    "XK",
    "ME",
    "KY",
    "YE",
    "LS",
    "ZW",
    "MC",
    "GN",
    "BS",
    "PF",
    "NA",
    "VI",
    "BB",
    "BZ",
    "CW",
    "PS",
    "FM",
    "PG",
    "BI",
    "AD",
    "TV",
    "GL",
    "KM",
    "AW",
    "TC",
    "CV",
    "MO",
    "VC",
    "NE",
    "WS",
    "MP",
    "DJ",
    "RW",
    "AG",
    "GI",
    "GQ",
    "AS",
    "AX",
    "TO",
    "KN",
    "LC",
    "NC",
    "LI",
    "SS",
    "IR",
    "SY",
    "IM",
    "SC",
    "VG",
    "SB",
    "DM",
    "KI",
    "UM",
    "SX",
    "GD",
    "MH",
    "BQ",
    "YT",
    "ST",
    "CF",
    "BM",
    "SM",
    "PW",
    "GU",
    "HK",
    "IN",
    "CK",
    "AQ",
    "WF",
    "JE",
    "MQ",
    "CN",
    "GF",
    "MS",
    "GG",
    "TK",
    "FK",
    "PM",
    "NU",
    "MF",
    "ER",
    "NF",
    "VA",
    "IO",
    "SH",
    "BL",
    "CU",
    "NR",
    "TP",
    "BV",
    "EH",
    "PN",
    "TF",
    "RU",
]
Fields = Literal[
    "create_date",
    "username",
    "region_code",
    "video_id",
    "hashtag_name",
    "keyword",
    "music_id",
    "effect_id",
    "video_length",
]
Operators = Literal["EQ", "IN", "GT", "GTE", "LT", "LTE"]


@dataclass
class Condition:
    """TikTok Research API Query Condition

    Args
    ----
    field_name: Fields
        Field to query
    operation: Operators
        Operator to use
    field_value: Union[str, int, List[str]]
        Value to compare against
    """

    field_name: Fields
    operation: Operators
    field_values: List[str]


@dataclass(config=ConfigDict(alias_generator=lambda x: x.removesuffix("_")))
class Query:
    """TikTok Research API Query

    Args
    ----

    and_: List[Condition]
        List of conditions that must all be true
    or_: List[Condition]
        List of conditions where at least one must be true
    not_: List[Condition]
        List of conditions that must all be false
    """

    and_: List[Condition] = field(default_factory=list)
    or_: List[Condition] = field(default_factory=list)
    not_: List[Condition] = field(default_factory=list)


def as_dict(query: Query):
    """Convert Query object to dictionary"""
    return RootModel(query).model_dump(by_alias=True)
