from datetime import datetime
from typing import List, Dict, Any
import json
from src.api.models import User, PainEvent

def map_user_to_patient(user: User) -> Dict[str, Any]:
    """
    Maps a User model to a FHIR Patient resource.
    """
    return {
        "resourceType": "Patient",
        "id": str(user.id),
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
        },
        "identifier": [{
            "system": "urn:pain-management-diary:patients",
            "value": str(user.id)
        }],
        "active": user.is_active,
        "name": [{
            "text": user.full_name or "Unknown"
        }],
        "telecom": [{
            "system": "email",
            "value": user.email,
            "use": "home"
        }],
        "managingOrganization": {
            "reference": "Organization/pain-management-diary"
        }
    }

def map_pain_event_to_observation(pain_event: PainEvent) -> Dict[str, Any]:
    """
    Maps a PainEvent model to a FHIR Observation resource.
    """
    return {
        "resourceType": "Observation",
        "id": str(pain_event.id),
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/Observation"]
        },
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "survey",
                "display": "Survey"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "72514-3",
                "display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported"
            }]
        },
        "subject": {
            "reference": f"Patient/{pain_event.user_id}"
        },
        "effectiveDateTime": pain_event.timestamp.isoformat(),
        "issued": pain_event.created_at.isoformat(),
        "valueQuantity": {
            "value": pain_event.severity,
            "unit": "{score}",
            "system": "http://unitsofmeasure.org",
            "code": "{score}"
        },
        "bodySite": [{
            "coding": [{
                "system": "urn:pain-management-diary:body-locations",
                "code": pain_event.location.lower().replace(" ", "-"),
                "display": pain_event.location
            }]
        }],
        "component": [
            {
                "code": {
                    "coding": [{
                        "system": "urn:pain-management-diary:observation-components",
                        "code": "symptoms",
                        "display": "Symptoms"
                    }]
                },
                "valueString": json.dumps(pain_event.symptoms)
            },
            {
                "code": {
                    "coding": [{
                        "system": "urn:pain-management-diary:observation-components",
                        "code": "triggers",
                        "display": "Triggers"
                    }]
                },
                "valueString": json.dumps(pain_event.triggers)
            }
        ],
        "note": [{
            "text": pain_event.notes or ""
        }]
    }

def create_fhir_bundle(user: User, pain_events: List[PainEvent]) -> Dict[str, Any]:
    """
    Creates a FHIR Bundle containing patient and observation resources.
    """
    resources = [map_user_to_patient(user)]
    resources.extend(map_pain_event_to_observation(event) for event in pain_events)

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.utcnow().isoformat(),
        "entry": [{"resource": resource} for resource in resources]
    }
