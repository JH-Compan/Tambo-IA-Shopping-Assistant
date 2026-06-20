def build_nlp_analysis(overrides=None):
    analysis = {
        "schema_version": "1.0",
        "intent": {
            "value": "consulta_general",
            "confidence": 0.0,
            "source": "unknown"
        },
        "need": {
            "value": None,
            "status": "not_mentioned",
            "confidence": 0.0,
            "source": "none"
        },
        "entities": {
            "product_id": None,
            "product_name": None,
            "brand": None,
            "category_id": None,
            "category_name": None,
            "promotion_id": None,
            "promotion_type": None,
            "quantity": 1,
            "budget_min": None,
            "budget_max": None
        },
        "preferences": [],
        "exclusions": {
            "product_ids": [],
            "products": [],
            "brands": [],
            "category_ids": [],
            "categories": []
        },
        "context": {
            "used_previous_turns": False,
            "referenced_message_id": None,
            "referenced_recommendation_id": None,
            "referenced_product_id": None,
            "referenced_promotion_id": None,
            "referenced_rank_position": None
        },
        "decision": {
            "requires_clarification": False,
            "clarification_field": None,
            "clarification_question": None,
            "next_action": "respond"
        },
        "metadata": {
            "processing_status": "pending",
            "nlp_method": "unknown",
            "entity_candidates": [],
            "category_candidates": [],
            "errors": []
        }
    }

    if overrides:
        _deep_update(analysis, overrides)

    return normalize_nlp_analysis(analysis)


def normalize_nlp_analysis(value):
    base = {
        "schema_version": "1.0",
        "intent": {
            "value": "consulta_general",
            "confidence": 0.0,
            "source": "unknown"
        },
        "need": {
            "value": None,
            "status": "not_mentioned",
            "confidence": 0.0,
            "source": "none"
        },
        "entities": {
            "product_id": None,
            "product_name": None,
            "brand": None,
            "category_id": None,
            "category_name": None,
            "promotion_id": None,
            "promotion_type": None,
            "quantity": 1,
            "budget_min": None,
            "budget_max": None
        },
        "preferences": [],
        "exclusions": {
            "product_ids": [],
            "products": [],
            "brands": [],
            "category_ids": [],
            "categories": []
        },
        "context": {
            "used_previous_turns": False,
            "referenced_message_id": None,
            "referenced_recommendation_id": None,
            "referenced_product_id": None,
            "referenced_promotion_id": None,
            "referenced_rank_position": None
        },
        "decision": {
            "requires_clarification": False,
            "clarification_field": None,
            "clarification_question": None,
            "next_action": "respond"
        },
        "metadata": {
            "processing_status": "pending",
            "nlp_method": "unknown",
            "entity_candidates": [],
            "category_candidates": [],
            "errors": []
        }
    }

    analysis = value if isinstance(value, dict) else {}
    normalized = _deep_update(base, {key: val for key, val in analysis.items() if key != "intent"})

    legacy_intent = analysis.get("intent")
    if isinstance(legacy_intent, str):
        normalized["intent"]["value"] = legacy_intent or "consulta_general"
        normalized["intent"]["confidence"] = _to_float(analysis.get("confidence"), 0.0)
        normalized["intent"]["source"] = analysis.get("source") or normalized["intent"]["source"]
    elif isinstance(legacy_intent, dict):
        normalized["intent"] = _normalize_section(legacy_intent, base["intent"])
        normalized["intent"]["confidence"] = _to_float(
            legacy_intent.get("confidence", analysis.get("confidence")),
            0.0
        )
    else:
        normalized["intent"]["value"] = normalized["intent"].get("value") or "consulta_general"
        normalized["intent"]["confidence"] = _to_float(
            normalized["intent"].get("confidence", analysis.get("confidence")),
            0.0
        )
        normalized["intent"]["source"] = normalized["intent"].get("source") or "unknown"

    normalized["preferences"] = _ensure_list(normalized.get("preferences"))

    exclusions = normalized.get("exclusions")
    exclusions = exclusions if isinstance(exclusions, dict) else {}
    normalized["exclusions"] = {
        "product_ids": _ensure_list(exclusions.get("product_ids")),
        "products": _ensure_list(exclusions.get("products")),
        "brands": _ensure_list(exclusions.get("brands")),
        "category_ids": _ensure_list(exclusions.get("category_ids")),
        "categories": _ensure_list(exclusions.get("categories")),
    }

    metadata = normalized.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    metadata["entity_candidates"] = _normalize_entity_candidates(metadata.get("entity_candidates"))
    metadata["category_candidates"] = _ensure_list(metadata.get("category_candidates"))
    metadata["errors"] = _ensure_list(metadata.get("errors"))
    metadata["processing_status"] = metadata.get("processing_status") or "pending"
    metadata["nlp_method"] = metadata.get("nlp_method") or metadata.get("analysis_method") or "unknown"
    normalized["metadata"] = metadata

    normalized["context"] = _normalize_section(normalized.get("context"), base["context"])
    normalized["decision"] = _normalize_section(normalized.get("decision"), base["decision"])
    normalized["entities"] = _normalize_section(normalized.get("entities"), base["entities"])
    normalized["need"] = _normalize_section(normalized.get("need"), base["need"])
    normalized["schema_version"] = normalized.get("schema_version") or "1.0"
    return normalized


def get_intent_value(analysis, default="consulta_general"):
    normalized = normalize_nlp_analysis(analysis)
    return normalized["intent"].get("value") or default


def get_intent_confidence(analysis, default=0.0):
    normalized = normalize_nlp_analysis(analysis)
    return _to_float(normalized["intent"].get("confidence"), default)


def _deep_update(target, overrides):
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
    return target


def _ensure_list(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _normalize_section(value, defaults):
    section = value if isinstance(value, dict) else {}
    result = dict(defaults)
    result.update(section)
    return result


def _normalize_entity_candidates(value):
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []

    normalized = []
    for entity_type, candidates in value.items():
        singular_type = str(entity_type or "").rstrip("s")
        for candidate in _ensure_list(candidates):
            if isinstance(candidate, dict):
                record = dict(candidate)
                record.setdefault("entity_type", record.get("type") or record.get("kind") or singular_type)
                normalized.append(record)
            else:
                normalized.append({
                    "entity_type": singular_type,
                    "value": candidate
                })
    return normalized


def _to_float(value, default):
    try:
        return float(value)
    except Exception:
        return float(default)
