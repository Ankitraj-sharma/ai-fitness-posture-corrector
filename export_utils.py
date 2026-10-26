"""
Export utilities for FitTrack AI workout sessions.
Formats rep counts, form accuracy, timestamps, and energy burn into exportable CSV/JSON reports.
"""

import json
import csv
import io
from typing import Dict, Any, List
from datetime import datetime


def export_session_to_csv(session_history: List[Dict[str, Any]]) -> str:
    """
    Exports workout session history records to a CSV string.
    """
    output = io.StringIO()
    fieldnames = ["timestamp", "exercise", "reps", "correct_reps", "incorrect_reps", "accuracy_pct", "calories_kcal"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for record in session_history:
        writer.writerow({
            "timestamp": record.get("timestamp", datetime.now().isoformat()),
            "exercise": record.get("exercise", "Unknown"),
            "reps": record.get("reps", 0),
            "correct_reps": record.get("correct_reps", 0),
            "incorrect_reps": record.get("incorrect_reps", 0),
            "accuracy_pct": round(record.get("accuracy", 0.0), 1),
            "calories_kcal": round(record.get("calories", 0.0), 2)
        })
    
    return output.getvalue()


def export_session_to_json(session_metadata: Dict[str, Any], history: List[Dict[str, Any]]) -> str:
    """
    Exports workout session with metadata to formatted JSON.
    """
    payload = {
        "app": "FitTrack AI",
        "exported_at": datetime.now().isoformat(),
        "metadata": session_metadata,
        "history": history
    }
    return json.dumps(payload, indent=2)
