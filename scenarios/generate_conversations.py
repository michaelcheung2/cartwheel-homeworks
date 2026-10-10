"""Write and independently critique conversations without calling Cartwheel.

Plans contain separate `scenario`, `grounding`, and `user_brief` objects.
Only user_brief reaches Ollama. Known identifiers are bound locally afterward,
so the writer never receives the database rows, answer key, or exact dates.
Each conversation and its critic use separate calls in a bounded worker pool.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import time
import urllib.request


SCHEMA = {
    "type": "object",
    "properties": {
        "opening_message": {"type": "string"},
        "followups": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["opening_message", "followups"],
    "additionalProperties": False,
}
STYLE_GUIDANCE = {
    "neutral_conversational": "One natural sentence per turn; no greeting or backstory.",
    "terse_fragmentary": "Use brief fragments, roughly six to twelve words per turn; omit polite padding.",
    "typo_heavy": "Keep it understandable but include two plausible spelling mistakes per turn. Do not misspell supplied entity names or placeholders.",
    "confused_rambling": "Sound unsure and slightly wordy, roughly twenty to forty words per turn, but add no events or personal backstory.",
    "frustrated_impatient": "Direct and impatient, roughly ten to twenty-five words per turn. Express urgency without inventing previous contact, delays, or events.",
    "repetitive_pressuring": "Briefly repeat the need or urgency within the message, without inventing history or claiming a previous action succeeded.",
    "operational_shorthand": "Use clipped operational fragments separated by punctuation, roughly six to fifteen words per turn.",
    "requests_short_plain_answer": "Ask the question naturally and explicitly ask for a short, plain answer; avoid jargon.",
}
WRITER = """Write one realistic conversation consisting ONLY of USER messages
to Cartwheel support. Follow the supplied role, goal, language style, and turn
count. Return opening_message and followups as JSON. Each followup adds detail
or asks a related question independently of any possible agent reply. Never
assume an action happened, an offer was made, or a question was asked. Preserve
the style in every turn. Do not invent order numbers, dates, amounts, names,
policy rules, tools, or account details. Supplied
store and product names are public facts. Cartwheel is a fictional marketplace,
unrelated to Target or any other company. Only mention names in the brief.
Write from the authenticated user's role: a shopper owns the order, a merchant
handles their store's customer orders, and support staff handle customer orders.
Do not mention internal evaluation
metadata. Make the request specific to the goal without predicting its answer.
Avoid canned openings such as 'Hi, I am reaching out' and unnecessary greetings.
"""
CRITIC = """Independently review this synthetic USER conversation. Return a
corrected opening_message and followups JSON, even if no change is necessary.
Preserve the brief's goal, role, style, and exact turn count. Remove invented
identifiers, amounts, dates, entity names, policy rules, or assumed prior agent
responses. Keep every subgoal from the brief, including questions about timing
or destination of a refund. Write from the correct role: merchants and support
staff handle customer orders rather than claiming a customer's order as theirs.
Cartwheel is a fictional marketplace unrelated to Target. Only use entity names
supplied in the brief. Ensure
each followup is plausible regardless of the preceding agent response and
does not repeat a state-changing instruction. Compare peer openings for canned
repetition and vary the phrasing if needed. Do not add tools, traces, prompts,
hidden outcomes, or internal policy terminology to user messages.
"""


def model_call(model: str, system: str, payload: dict) -> tuple[dict, dict]:
    brief = payload["brief"]
    required_followups = brief["turn_count"] - 1
    schema = json.loads(json.dumps(SCHEMA))
    schema["properties"]["followups"].update(minItems=required_followups, maxItems=required_followups)
    system += f"\nReturn exactly {required_followups} followups, in addition to one opening message."
    if brief.get("draft_messages"):
        system += """\nThe brief includes draft_messages, one USER message per turn.
Use those as the conversation outline. Rephrase naturally into the assigned style,
preserving the requested action and every factual entity. Do not add a backstory,
invent purchases/delivery/refund status, change the intent, or write an assistant
response. Merchant 'our store order' and support 'customer order' stay distinct
from shopper 'my order'. Preserve every literal placeholder in its original turn.
Terse and shorthand styles stay short; typo-heavy style retains plausible typos;
confused style may be wordier; pressure/frustration stays direct without adding
claims about previous events. When reviewing, use the outline to correct drift.
"""
    system += "\nApply this language style in EVERY turn: " + STYLE_GUIDANCE[brief["user_style"]]
    system += "\nMaximum sixty words in any user message. Never copy a canned opening across unrelated conversations."
    if brief.get("order_reference"):
        system += " Include the literal token {{ORDER}} once in the opening; it represents a known receipt number and will be filled locally."
    else:
        system += " This request has NO order reference: never include any placeholder, order number, receipt reference, or {{ORDER}} token."
    if brief.get("allowed_placeholders"):
        system += " Allowed literal tokens: " + ", ".join(brief["allowed_placeholders"]) + ". Keep every supplied token, without inventing its value."
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload)},
        ],
        "stream": False,
        "format": schema,
        "options": {"temperature": 0.8, "num_predict": 650, "num_ctx": 4096},
        "keep_alive": "30m",
    }).encode()
    request = urllib.request.Request(
        "http://localhost:11434/api/chat", data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        observed = json.load(response)
    return json.loads(observed["message"]["content"]), observed


def check(conversation: dict, brief: dict) -> None:
    opening = conversation.get("opening_message")
    followups = conversation.get("followups")
    if not isinstance(opening, str) or not opening.strip():
        raise ValueError("missing opening_message")
    if not isinstance(followups, list) or len(followups) != brief["turn_count"] - 1:
        raise ValueError("incorrect followup count")
    if any(not isinstance(s, str) or not s.strip() for s in followups):
        raise ValueError("empty followup")
    if brief.get("order_reference") and "{{ORDER}}" not in opening:
        raise ValueError("missing receipt placeholder")
    if not brief.get("order_reference") and any("{{" in s for s in [opening, *followups]):
        raise ValueError("unexpected placeholder: this request has no order reference")
    for message in [opening, *followups]:
        if brief.get("draft_messages") and len(message.split()) > 60:
            raise ValueError("overlong message: at most sixty words per turn, with no invented backstory")
        # User briefs intentionally have no numbers; known IDs are bound later.
        if re.search(r"\d", message):
            raise ValueError("writer invented a number")
        if re.search(r"\b(Target|Walmart|Amazon|eBay|Mary Oliver)\b", message, re.IGNORECASE):
            raise ValueError("invented entity name: only use names supplied in the brief")
    for token in brief.get("allowed_placeholders", []):
        if token not in " ".join([opening, *followups]):
            raise ValueError("missing user-known placeholder: " + token)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plans", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", default="llama3.1:8b")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--edits", type=Path, help="Apply recorded editorial corrections after binding identifiers")
    args = parser.parse_args()
    if args.workers < 2:
        parser.error("use at least two workers")
    plans = [json.loads(line) for line in args.plans.read_text().splitlines() if line]
    args.audit.mkdir(parents=True, exist_ok=True)
    drafts: dict[str, dict] = {}
    reviewed: dict[str, dict] = {}

    def perform(plan: dict, stage: str, peers: list[str] | None = None) -> dict:
        identifier = plan["scenario"]["id"]
        audit_file = args.audit / f"{identifier}-{stage}.json"
        if audit_file.exists():
            saved = json.loads(audit_file.read_text())
            if saved["brief"] != plan["user_brief"] or saved["model"] != args.model:
                raise ValueError(f"{identifier}: cached generation belongs to another plan/model")
            conversation = saved["conversation"]
            try:
                check(conversation, plan["user_brief"])
            except ValueError:
                # Preserve the rejected draft while regenerating only this row.
                audit_file.rename(args.audit / f"{identifier}-{stage}-rejected.json")
            else:
                return conversation
        payload = {"brief": plan["user_brief"]}
        if stage == "critic":
            payload.update(conversation=drafts[identifier], peer_openings=peers)
        for attempt in range(5):
            conversation, observed = model_call(
                args.model, WRITER if stage == "writer" else CRITIC, payload,
            )
            try:
                check(conversation, plan["user_brief"])
            except ValueError as error:
                # Save unsuccessful calls too; retries are visible in the audit.
                (args.audit / f"{identifier}-{stage}-attempt{attempt}-{time.time_ns()}.json").write_text(
                    json.dumps({"payload": payload, "observed": observed, "error": str(error)}, indent=2)
                )
                payload["repair_instruction"] = str(error)
                continue
            audit_file.write_text(json.dumps({
                "brief": plan["user_brief"], "model": args.model,
                "payload": payload, "conversation": conversation,
                "observed": observed,
            }, indent=2))
            return conversation
        raise ValueError(f"{identifier}: {stage} failed five structural checks")

    for stage, results in [("writer", drafts), ("critic", reviewed)]:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            tasks = {}
            for plan in plans:
                identifier = plan["scenario"]["id"]
                peers = [draft["opening_message"] for key, draft in drafts.items()
                         if key != identifier][:12] if stage == "critic" else None
                tasks[pool.submit(perform, plan, stage, peers)] = identifier
            for task in as_completed(tasks):
                identifier = tasks[task]
                results[identifier] = task.result()
                print(f"{stage} {len(results)}/{len(plans)} {identifier}", flush=True)

    scenarios = []
    for plan in plans:
        scenario = dict(plan["scenario"])
        conversation = reviewed[scenario["id"]]
        messages = [conversation["opening_message"], *conversation["followups"]]
        for token, value in plan.get("bindings", {}).items():
            messages = [message.replace(token, str(value)) for message in messages]
        if any("{{" in message for message in messages):
            raise ValueError(f"{scenario['id']}: unbound placeholder")
        scenario.update(opening_message=messages[0], followups=messages[1:])
        scenarios.append(scenario)
    if args.edits:
        edits = json.loads(args.edits.read_text())
        for scenario in scenarios:
            edit = edits.get(scenario["id"])
            if edit:
                current = {key: scenario[key] for key in ["opening_message", "followups"]}
                if current != edit["before"]:
                    raise ValueError(f"{scenario['id']}: editorial correction belongs to a different draft")
                if len(edit["after"]["followups"]) + 1 != scenario["tuple"]["turn_count"]:
                    raise ValueError(f"{scenario['id']}: editorial correction changes turn count")
                scenario.update(edit["after"])
    args.output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in scenarios))
    print(f"Saved {len(scenarios)} independently generated and critiqued conversations to {args.output}")


if __name__ == "__main__":
    main()
