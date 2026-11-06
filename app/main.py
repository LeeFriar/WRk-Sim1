from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel


class NotableIncident(BaseModel):
    """A representative Splunk Enterprise Security notable event."""

    id: str
    rule_name: str
    event_title: str
    description: str
    severity: str
    status: str
    urgency: str
    owner: str
    source: str
    destination: str
    defender_id: str
    username: str
    hostname: str
    incidentId: str
    accountUpn: str
    deviceName: str
    category: str
    mitre_technique: str
    created_at: datetime
    updated_at: datetime


class IncidentResponse(BaseModel):
    count: int
    generated_at: datetime
    incidents: list[NotableIncident]


app = FastAPI(
    title="Splunk Notable Incident Simulator",
    description="Generates realistic sample notable incidents for integration testing.",
    version="1.0.0",
)

RULES = [
    ("Excessive Failed Logins", "Multiple authentication failures detected", "medium", "T1110", "Credential Access"),
    ("Suspicious PowerShell Activity", "Encoded or unusual PowerShell command detected", "high", "T1059.001", "Execution"),
    ("Potential Data Exfiltration", "Unusually large outbound transfer detected", "critical", "T1041", "Exfiltration"),
    ("Malware Beaconing", "Periodic connection to a suspicious external host detected", "high", "T1071.001", "Command and Control"),
    ("Privilege Escalation Attempt", "Unexpected privileged group membership change detected", "high", "T1098", "Persistence"),
    ("Suspicious Cloud API Usage", "Unusual cloud control-plane activity detected", "medium", "T1078.004", "Initial Access"),
    ("Endpoint Defense Impairment", "Attempt to disable endpoint protection detected", "critical", "T1562.001", "Defense Evasion"),
    ("Unusual DNS Query", "High-entropy DNS query pattern detected", "low", "T1071.004", "Command and Control"),
]
USERNAMES = [
    "j.smith", "a.patel", "m.chen", "svc-backup", "d.jones", "unknown", "r.wilson", "k.brown",
    "s.garcia", "t.miller", "n.davis", "p.thompson", "l.white", "c.harris", "e.clark", "b.lewis",
    "svc-deploy", "svc-monitor", "admin.local", "guest.user",
]
HOSTNAMES = [
    "ws-104", "srv-app-02", "db-prod-01", "laptop-lee", "web-03", "ws-212", "srv-file-01", "db-test-02",
    "vpn-gw-01", "mail-02", "dc-01", "ws-317", "build-agent-04", "app-prod-03", "jumpbox-01", "nas-02",
    "k8s-node-05", "ws-088", "proxy-01", "10.20.4.18",
]
DEFENDER_IDS = [f"{number:08x}-1a2b-4c3d-8e9f-{number:012x}" for number in range(1, 51)]
DESTINATIONS = ["198.51.100.24", "203.0.113.17", "updates.example.net", "10.20.8.9", "185.199.108.153"]
SOURCES = ["WinEventLog:Security", "Sysmon", "CrowdStrike:FDR", "aws:cloudtrail", "suricata"]


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    return {
        "service": "Splunk Notable Incident Simulator",
        "docs": "/docs",
        "health": "/health",
        "incidents": "/api/incidents",
    }


@app.get("/health", tags=["service"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/incidents", response_model=IncidentResponse, tags=["incidents"])
def get_incidents(
    count: Annotated[int | None, Query(ge=1, le=5, description="Optional exact number of incidents")]=None,
    seed: Annotated[int | None, Query(description="Optional deterministic seed for repeatable tests")]=None,
) -> IncidentResponse:
    rng = random.Random(seed)
    total = count if count is not None else rng.randint(1, 5)
    now = datetime.now(timezone.utc)
    incidents: list[NotableIncident] = []
    usernames = [rng.choice(USERNAMES) for _ in range(total)]
    hostnames = [rng.choice(HOSTNAMES) for _ in range(total)]

    for index in range(total):
        rule, title, severity, technique, category = rng.choice(RULES)
        created = now - timedelta(minutes=rng.randint(1, 1440))
        defender_id = rng.choice(DEFENDER_IDS)
        username = usernames[index]
        hostname = hostnames[index]
        incidents.append(
            NotableIncident(
                id=f"notable-{now:%Y%m%d}-{rng.randrange(100000, 999999)}-{index + 1}",
                rule_name=rule,
                event_title=title,
                description=f"{title} on {hostnames[index]} involving {usernames[index]}.",
                severity=severity,
                status=rng.choice(["new", "in_progress", "pending", "resolved"]),
                urgency="high" if severity == "critical" else severity,
                owner=rng.choice(["unassigned", "soc_analyst_1", "soc_analyst_2"]),
                source=rng.choice(SOURCES),
                destination=rng.choice(DESTINATIONS),
                defender_id=defender_id,
                username=username,
                hostname=hostname,
                incidentId=defender_id,
                accountUpn=username,
                deviceName=hostname,
                category=category,
                mitre_technique=technique,
                created_at=created,
                updated_at=created + timedelta(minutes=rng.randint(0, 60)),
            )
        )

    return IncidentResponse(count=total, generated_at=now, incidents=incidents)
