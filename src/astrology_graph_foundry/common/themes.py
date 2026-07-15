from __future__ import annotations
from .io import clean_body_name

THEME_TRIGGERS={
"communication":{"Mercury","Gemini","3"},"emotional_safety":{"Moon","Cancer","4"},"romance_affection":{"Venus","Leo","5"},
"conflict_drive":{"Mars","Aries"},"growth_meaning":{"Jupiter","Sagittarius","9"},"commitment_structure":{"Saturn","Capricorn"},
"freedom_change":{"Uranus","Aquarius"},"dream_idealization":{"Neptune","Pisces"},"depth_power":{"Pluto","Scorpio","8"},
"identity_visibility":{"Sun","ASC","MC","Leo","1","10"},"partnership_mirroring":{"DSC","Libra","7"},"home_family":{"IC","Cancer","4"},
"values_resources":{"Venus","Taurus","2"}}
OPERATOR_HINTS={"Sun":["illuminate","prioritize","express"],"Moon":["regulate","need","remember"],"Mercury":["represent","translate","interpret","compare"],"Venus":["connect","attract","value","bond"],"Mars":["act","assert","defend","initiate"],"Jupiter":["contextualize","expand","synthesize","encourage"],"Saturn":["stabilize","constrain","endure","structure"],"Uranus":["differentiate","liberate","disrupt","individuate"],"Neptune":["imagine","dissolve","idealize","spiritualize"],"Pluto":["intensify","transform","expose","empower"],"ASC":["interface","present","enter"],"DSC":["mirror","partner","externalize"],"MC":["publicize","aspire","direct"],"IC":["root","secure","privatize"]}

def theme_tags(*tokens: object, aspect: str | None=None) -> list[str]:
    t={clean_body_name(x) for x in tokens if x is not None}
    tags=[tag for tag,triggers in THEME_TRIGGERS.items() if t & triggers]
    if aspect in {"square","opposition","quincunx"}: tags.append("growth_edge")
    if aspect in {"trine","sextile"}: tags.append("ease_support")
    if aspect=="conjunction": tags.append("fusion_intensity")
    return sorted(set(tags))

def operator_hints(*bodies: object, aspect: str | None=None) -> list[dict]:
    hints=[]
    for body in bodies:
        clean=clean_body_name(body)
        for op in OPERATOR_HINTS.get(clean,[]):
            hints.append({"body":clean,"operator":op,"source":f"{clean} operator family"})
    for op in {"conjunction":["merge","amplify"],"opposition":["polarize","mirror","negotiate"],"square":["stress","activate","develop"],"trine":["flow","support"],"sextile":["cooperate","enable"],"quincunx":["adjust","recalibrate"],"semisextile":["nudge","adjacent-adjust"]}.get(aspect,[]):
        hints.append({"body":"aspect","operator":op,"source":f"{aspect} aspect primitive"})
    return hints
