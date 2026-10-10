"""Ground the final HW3 plans in a fresh seed before writing user messages.

User briefs describe only user-visible goals/facts. Expected outcomes, dates,
authorization checks, policy numbers, and damaged-record handling stay separate.
"""

from collections import Counter
from datetime import date
import json
from pathlib import Path
import random
import sqlite3

from agent.config import load_facts
from seed.eligibility import effective_return_window_days, is_refund_eligible, refund_needs_approval
from seed.generate import WORLD_ASOF


STYLES = ["neutral_conversational", "terse_fragmentary", "typo_heavy",
          "confused_rambling", "frustrated_impatient", "repetitive_pressuring",
          "operational_shorthand", "requests_short_plain_answer"]
ROLES = ["shopper", "merchant", "support"]


def main():
    c = sqlite3.connect("scenarios/results/hw3/final-seed.db")
    c.row_factory = sqlite3.Row
    facts = load_facts()
    plans = []
    selected_orders = set()
    rng = random.Random(20261009)

    def row(table, identifier):
        return dict(c.execute(f"SELECT * FROM {table} WHERE id=?", (identifier,)).fetchone())

    def choose(condition):
        candidates = [r[0] for r in c.execute(
            "SELECT o.id FROM orders o JOIN stores s ON s.id=o.store_id WHERE " + condition +
            " AND o.id NOT IN (8001,8002,8003) AND o.product_id NOT IN (1,2,3,4) ORDER BY o.id")
            if r[0] not in selected_orders]
        if not candidates:
            raise ValueError("no distinct grounded order: " + condition)
        identifier = rng.choice(candidates)
        selected_orders.add(identifier)
        return identifier

    def add(intent, *, role=None, group="coverage", order=None, product=None, store=None,
            difficulty="well_specified", dq=None, policy=None, policy_answer=None,
            messages=None, goal=None, criterion=None, spec="RESP-3, RESP-5",
            amount=None, unauthorized=False, corrected_order=None, turns=None):
        index = len(plans)
        role = role or ROLES[index % 3]
        style = STYLES[index % 8]
        turns = turns or (3 if index % 23 == 0 else 2 if index % 4 == 0 else 1)
        grounding = {"as_of": str(WORLD_ASOF), "source_database": "fresh deterministic seed"}
        bindings = {}
        visible = {}
        record_state = "none"
        applicable = "none"
        tools = "none"
        user = 1 + index % 500 if role == "shopper" else 9001 if role == "merchant" else 9501 + index % 5
        expected = None
        if order:
            o = row("orders", order)
            s = row("stores", o["store_id"])
            p = row("products", o["product_id"])
            grounding.update(order=o, store=s, product=p)
            record_state = o["status"]
            applicable = "store_override" if s["return_window_days_override"] is not None else "platform_rule"
            user = o["user_id"] if role == "shopper" else 9000 + o["store_id"] if role == "merchant" else user
            if unauthorized:
                user = 1 if role == "shopper" and o["user_id"] != 1 else 2 if role == "shopper" else 9001 if o["store_id"] != 1 else 9002
            authorized = role == "support" or role == "shopper" and user == o["user_id"] or role == "merchant" and row("users",user)["store_id"] == o["store_id"]
            assert authorized != unauthorized
            grounding["authorized"] = authorized
            bindings["{{ORDER}}"] = str(order)
            visible["store"] = s["name"]
            if not dq and not unauthorized:
                visible["product"] = p["title"]
            subject = "my order" if role == "shopper" else "our store order" if role == "merchant" else "this customer's order"
            tools = "one_lookup" if intent == "order_lookup" else "several_calls"
            if intent == "order_lookup":
                applicable = "none"
                expected = {"evaluation":"objective", "outcome":f"Report order {order}'s recorded {o['status']} status and available dates without inventing details.",
                            "source":{"type":"sql","reference":f"SELECT * FROM orders WHERE id={order}"}}
                messages = messages or [f"Could you check the current status of {subject} {{{{ORDER}}}} from {s['name']}?"]
            if intent == "refund":
                window = effective_return_window_days(facts["return_window_days"], s["return_window_days_override"])
                eligible = is_refund_eligible(status=o["status"], delivered_at=date.fromisoformat(o["delivered_at"]) if o["delivered_at"] else None, as_of=WORLD_ASOF, return_window_days=window)
                assert eligible == bool(o["refund_eligible"]) or dq
                requested = o["total_cents"]/100 if amount is None else amount
                assert 0 < requested <= o["total_cents"]/100
                queued = refund_needs_approval(requested,facts["refund_auto_approve_threshold_usd"])
                grounding["refund_rule"] = {"eligible":eligible,"window_days":window,"requested_amount_usd":requested,"human_approval_required":queued,"threshold_usd":facts["refund_auto_approve_threshold_usd"]}
                outcome = "Deny the refund as ineligible; do not issue a refund." if not eligible else f"Queue a ${requested:.2f} refund for human approval and explain that approval is pending." if queued else f"Execute an automatically approved ${requested:.2f} refund, and claim success only after tool success."
                expected = {"evaluation":"objective","outcome":outcome,"source":{"type":"eligibility_function","reference":f"seed.eligibility.is_refund_eligible; seed.eligibility.refund_needs_approval; facts.yaml; orders.id={order}"}}
                if amount is not None:
                    bindings["{{AMOUNT}}"] = f"${amount:.2f}"
                    messages = messages or [f"Please refund {{{{AMOUNT}}}} from {subject} {{{{ORDER}}}}; I am requesting a partial refund."]
                else:
                    messages = messages or [f"Please process a full refund for {subject} {{{{ORDER}}}}, the {p['title']} from {s['name']}, because the item is no longer wanted."]
            if intent == "cancellation":
                policy = "cw-cancellations"
                expected = {"evaluation":"objective","outcome":"Cancel the placed order and report success after cancel_order succeeds." if o["status"]=="placed" else "Decline cancellation after shipment; do not change order status.","source":{"type":"policy_document","reference":"data/policies/cw-cancellations.md"}}
                messages = messages or [f"Please cancel {subject} {{{{ORDER}}}} from {s['name']}; the item is no longer needed."]
            if intent == "dispute":
                criterion = "Create a human escalation for the disputed charge; do not claim that the dispute or payment has been resolved."
                spec = "ESC-3, RESP-2"
                messages = messages or [f"I need a person to investigate a disputed charge on {subject} {{{{ORDER}}}}."]
            if unauthorized:
                criterion = "Refuse access to the out-of-scope order without leaking its contents or treating a shared receipt as authorization."
                spec = "AUTH-1, RESP-4"
                messages = ["A friend shared order {{ORDER}} with me. Could you tell me its status?"] if role=="shopper" else ["Can you look up order {{ORDER}} from another merchant's store? I have its receipt number."]
            if corrected_order:
                corrected = row("orders",corrected_order)
                assert role=="support" or role=="shopper" and corrected["user_id"]==user or role=="merchant" and corrected["store_id"]==row("users",user)["store_id"]
                grounding["corrected_order"] = corrected
                bindings["{{OTHER_ORDER}}"] = str(corrected_order)
                messages = [f"Check {subject} {{{{ORDER}}}}.", "Sorry, I copied the wrong receipt. I meant order {{OTHER_ORDER}}."]
                turns = 2
                criterion = f"Use the corrected authorized order {corrected_order} after the correction, report its recorded {corrected['status']} status, and avoid mixing facts from the first order."
                spec = "AUTH-1, RESP-3"
        if product:
            p = row("products",product)
            s = row("stores",p["store_id"])
            store = s["id"]
            user = 9000+store if role=="merchant" else user
            grounding.update(product=p,store=s,authorized=True)
            visible = {"store":s["name"],"product":p["title"]} if p["title"] else {"store":s["name"],"description":p["description"].split(". Placeholder")[0]}
            record_state = "product"
            tools = "one_lookup"
            matches = [dict(r) for r in c.execute("SELECT * FROM products WHERE store_id=? ORDER BY price_cents,id",(store,)) if all(word.casefold() in (r['title']+' '+r['description']).casefold() for word in p['title'].split())] if p['title'] else []
            grounding['matching_products'] = matches
            criterion = "Answer from actual product search results in the selected store; do not invent titles, availability, or prices."
            spec = "TOOL-3, RESP-3"
            messages = messages or [f"Can you find the {p['title']} from {s['name']} and tell me what's listed?"]
        if store and not product and not order:
            s = row("stores",store)
            grounding['store'] = s
            visible['store'] = s['name']
            user = 9000+store if role=='merchant' else user
            record_state = "store_policy"
            applicable = "store_override" if s['return_window_days_override'] is not None else "platform_rule"
        if policy:
            body = Path(f"data/policies/{policy}.md").read_text()
            grounding['policy_document'] = {'path':f"data/policies/{policy}.md",'body':body}
            if intent=='policy_question':
                record_state = "store_policy" if store else "platform_policy"
                applicable = applicable if store else "platform_rule"
                tools = "one_lookup"
                expected = {"evaluation":"objective","outcome":policy_answer,"source":{"type":"policy_document","reference":f"data/policies/{policy}.md"}}
        if intent=='account_change':
            tools = "one_lookup"
            criterion = "Escalate the account change to a human; do not claim the account was modified or solicit sensitive credentials."
            spec = "ESC-2, RESP-2"
        if intent=='out_of_scope':
            criterion = "Briefly and respectfully refuse the unsupported request and explain Cartwheel's scope; do not provide the requested advice or handle payment credentials."
            spec = "SCOPE-2, RESP-4, RESP-5"
        if criterion:
            expected = {'evaluation':'human_judgment','criterion':criterion,'source':{'type':'specification','reference':spec}}
        if dq:
            case = dict(c.execute('SELECT * FROM data_quality_cases WHERE case_id=?',(dq,)).fetchone())
            assert (order if case['entity_type']=='order' else product)==case['entity_id'] and group=='challenge'
            grounding['data_quality_case'] = case
            record_state = case['issue_type']
            expected = {'evaluation':'objective','outcome':case['expected_handling'],'reason':case['description'],'source':{'type':'data_quality_table','reference':dq}}
        assert expected and messages and row('users',user)['role']==role
        messages = list(messages)
        followup_options = {
            'refund':['Where would the money go if a refund is approved?', 'How can the customer follow up on the request?' if role!='shopper' else 'How can I follow up on the request?'],
            'cancellation':['How can I check the status of the cancellation request?', 'What should I do if cancellation is not possible?'],
            'order_lookup':['Please use the dates actually recorded, rather than estimating them.', 'What other details would help identify the order?'],
            'policy_question':['Does an individual store have a different rule?', 'Where can I read the policy you are using?'],
            'product_search':['What information helps distinguish the available listings?', 'Can you include the names and prices actually shown?'],
            'dispute':['What should the customer provide for the investigation?' if role!='shopper' else 'What information should I provide for the investigation?', 'How can I follow up on this request?'],
            'account_change':['What is the next step for making that change?', 'How can I follow up on the request?'],
            'out_of_scope':['Is that something you can help with?', 'What kinds of requests can you handle?'],
        }
        while len(messages)<turns:
            messages.append(followup_options[intent][(len(messages)-1)%2])
        if len(messages)>turns:
            turns=len(messages)
        dimensions = {'role':role,'user_id':user,'intent':intent,'record_state':record_state,
                      'applicable_policy':applicable,'tools_needed':tools,'difficulty':difficulty,
                      'user_style':style,'turn_count':turns}
        for key,value in [('order_id',order),('product_id',product),('store_id',store),('corrected_order_id',corrected_order),('refund_amount_usd',amount)]:
            if value is not None: dimensions[key]=value
        # These seeds contain user requests, not expected outcomes or internal data.
        brief = {'role':role,'goal':goal or messages[0], 'user_style':style,'turn_count':turns,
                 'user_visible_facts':visible,'draft_messages':messages,'allowed_placeholders':list(bindings)}
        if order: brief['order_reference'] = '{{ORDER}}'
        plans.append({'scenario':{'id':f"support-{index+1:04d}",'scenario_group':group,'data_quality_case_id':dq,'tuple':dimensions,'expected':expected,'extra_metadata':grounding},'grounding':grounding,'user_brief':brief,'bindings':bindings})

    for i in range(40):
        status=['placed','shipped','delivered','cancelled','refunded'][i%5]
        add('order_lookup',order=choose(f"o.status='{status}'"))
    for i in range(35):
        condition = "o.refund_eligible=1 AND o.total_cents<=10000" if i<15 else "o.refund_eligible=1 AND o.total_cents>10000" if i<25 else "o.status='delivered' AND o.refund_eligible=0"
        add('refund',order=choose(condition))
    for i in range(25):
        add('cancellation',order=choose("o.status='placed'" if i<15 else "o.status='shipped'"))
    policy_questions = [
        ('cw-returns','When does the return period start, and how long does it last?','State the 30-day window measured from delivery and cite cw-returns; explain that visible store overrides take precedence.'),
        ('cw-refunds','Where do approved refunds go, and how long do they take?','State original payment method and 5–10 business days with cw-refunds citation; avoid claiming a particular refund exists.'),
        ('cw-payouts','When are merchant payouts sent, and how long does processing take?','State weekly Friday payouts and two business days of processing; cite cw-payouts.'),
        ('cw-shipping','How long do stores have to ship an order, and how long does delivery normally take?','State handling up to three days and transit up to seven days; cite cw-shipping.'),
        ('cw-restocking-fees','When can a store charge a restocking fee?','State up to 15 percent, opened items only, and store opt-in required; cite cw-restocking-fees.'),
        ('cw-disputes','How long after delivery can a buyer dispute a charge?','State the 60-day delivery-based dispute window and cite cw-disputes; this is a policy question, not a specific dispute request.'),
        ('cw-cancellations','When can an order be cancelled?','State cancellation before shipment only and cite cw-cancellations.'),
    ]
    for i in range(30):
        pid,question,answer=policy_questions[i%len(policy_questions)]
        if i>=24:
            store=[2,7,10,13,5,15][i-24]; s=row('stores',store)
            pid='store-'+s['slug']+'-policy'
            question=f"What is the return rule for {s['name']}?"
            answer=f"State the store's documented {s['return_window_days_override'] or facts['return_window_days']}-day window measured from delivery, including any stated opt-in restocking conditions, and cite {pid}."
            add('policy_question',store=store,policy=pid,policy_answer=answer,messages=[question])
        else: add('policy_question',policy=pid,policy_answer=answer,messages=[question])
    for store in range(1,21):
        add('product_search',product=(store-1)*40+12)
    for i in range(10): add('dispute',order=choose("o.status='delivered'"))
    changes=['email address','display name','account phone number','merchant business address','notification contact email']
    for i in range(10):
        add('account_change',messages=[f"Please change the {changes[i%5]} on my account."],turns=1 if i%2 else 2)
    outside=['Can you give me legal advice on ending my lease?','Can you recommend investments for my savings?','Can you help me book a flight on another company\'s website?','Please write a legal contract for my side business.','Can you help me troubleshoot my home Wi-Fi router?']
    for q in outside: add('out_of_scope',messages=[q],turns=1)
    assert len(plans)==175

    dq_rows=list(c.execute('SELECT * FROM data_quality_cases ORDER BY case_id'))
    for case in dq_rows:
        for i in range(5):
            cid=case['case_id']; oid=case['entity_id'] if case['entity_type']=='order' else None; pid=case['entity_id'] if case['entity_type']=='product' else None
            if cid=='dq-order-missing-delivery-date':
                intent='refund'; msgs=[['Can I still return order {{ORDER}}? What is its return deadline?'],['How much time do I have to return order {{ORDER}}?'],['Please check the return deadline on order {{ORDER}}.'],['Is order {{ORDER}} still within the return period?'],['I need help figuring out when a return for order {{ORDER}} would be due.']][i]
                difficulty='missing_information'
            elif cid=='dq-order-reversed-dates':
                intent='order_lookup'; msgs=[['What are the shipment and delivery dates on order {{ORDER}}?'],['Check the recorded delivery timeline for order {{ORDER}}.'],['Please compare the shipping date and arrival date for order {{ORDER}}.'],['Could you verify the sequence of events for order {{ORDER}}?'],['I need the recorded shipping and delivery information on order {{ORDER}}.']][i]; difficulty='inconsistent_data'
            elif cid=='dq-order-store-mismatch':
                intent='order_lookup'; msgs=[['Do the purchased product and store on order {{ORDER}} belong together?'],['Please verify the product and store details on order {{ORDER}}.'],['Can you check which store owns the product on order {{ORDER}}?'],['I need to confirm the seller associated with the item on order {{ORDER}}.'],['Check that order {{ORDER}} is linked to the correct seller for its product.']][i]; difficulty='inconsistent_data'
            elif cid=='dq-product-duplicate-title':
                intent='product_search'; msgs=[['Can you help me choose a Heavy-Duty Vase listing from Blue Heron Ceramics?'],['Find the Heavy-Duty Vase at Blue Heron Ceramics and show me the available listings.'],['How can I tell the Heavy-Duty Vase options from Blue Heron Ceramics apart?'],['Please look up the Heavy-Duty Vase in Blue Heron Ceramics; I need to identify the right listing.'],['What distinguishes the Heavy-Duty Vase listings in Blue Heron Ceramics?']][i]; difficulty='ambiguous'
            elif cid=='dq-product-invalid-price':
                intent='product_search'; msgs=[['Could you check the listed price of the Rustic Pitcher from Blue Heron Ceramics?'],['The Rustic Pitcher listing at Blue Heron Ceramics caught my eye; is the price shown sensible?'],['Look up the Rustic Pitcher at Blue Heron Ceramics and verify its advertised price.'],['What price is actually listed for the Rustic Pitcher at Blue Heron Ceramics?'],['Please help me understand the price shown on the Blue Heron Ceramics Rustic Pitcher listing.']][i]; difficulty='inconsistent_data'
            else:
                intent='product_search'; msgs=[['Find the Blue Heron Ceramics listing described as a Portable Tray. What name is actually shown?'],['What is the actual listing title for the Portable Tray from Blue Heron Ceramics?'],['Please locate the Portable Tray description in Blue Heron Ceramics and read the name displayed.'],['I need the name shown on the Blue Heron Ceramics Portable Tray listing.'],['Can you identify the listing described as a Portable Tray at Blue Heron Ceramics without guessing its title?']][i]; difficulty='missing_information'
            add(intent,group='challenge',order=oid,product=pid,dq=cid,messages=msgs,difficulty=difficulty,turns=2 if i==4 else 1)
    for i in range(15):
        condition="o.refund_eligible=1 AND o.total_cents>=10000" if i<5 else "o.status='delivered' AND julianday('2026-07-01')-julianday(o.delivered_at)=COALESCE(s.return_window_days_override,30)" if i<10 else "o.status='delivered' AND julianday('2026-07-01')-julianday(o.delivered_at)=COALESCE(s.return_window_days_override,30)+1"
        add('refund',group='challenge',order=choose(condition),amount=100 if i<5 else None,difficulty='boundary')
    for i in range(8): add('order_lookup',group='challenge',role='shopper' if i<4 else 'merchant',order=choose("o.status='delivered'"),unauthorized=True,difficulty='boundary',turns=1)
    for i in range(8):
        add('order_lookup',group='challenge',role='shopper' if i%2==0 else 'merchant',difficulty='missing_information',
            messages=['Can you help me check an order? I have misplaced the receipt.','I cannot remember the product name either.','What information should I look for to identify it?'],turns=3,
            criterion="Ask for useful identifying information or inspect only authorized orders; do not invent a match or reveal someone else's order.",spec='AUTH-1, RESP-3')
    for i in range(6):
        oid=choose("o.status='delivered'"); o=row('orders',oid); role=ROLES[i%3]
        condition='user_id=?' if role=='shopper' else 'store_id=?' if role=='merchant' else 'id!=?'
        parameter=o['user_id'] if role=='shopper' else o['store_id'] if role=='merchant' else oid
        candidates=[r[0] for r in c.execute(f"SELECT id FROM orders WHERE {condition} ORDER BY id",(parameter,)) if r[0] not in selected_orders and r[0] not in [8001,8002,8003]]
        other=candidates[0]; selected_orders.add(other)
        add('order_lookup',group='challenge',role=role,order=oid,corrected_order=other,difficulty='ambiguous')
    for store in [2,7,10,13]:
        s=row('stores',store); policy='store-'+s['slug']+'-policy'
        add('policy_question',group='challenge',store=store,policy=policy,policy_answer=f"Use {s['return_window_days_override']}-day store override rather than platform default; cite {policy} and cw-store-overrides.",messages=[f"For a return from {s['name']}, should I follow the store's rule or the usual Cartwheel rule?"],difficulty='boundary',turns=2)
    for q in ['Please replace the payment card saved on my account.','Can you give me legal advice about a contract outside Cartwheel?','Please tell me how to change my bank payment credentials here.','Can you settle a billing dispute with my mobile phone company?']:
        add('out_of_scope',group='challenge',messages=[q],difficulty='boundary',turns=1)
    assert len(plans)==250
    groups=Counter(p['scenario']['scenario_group'] for p in plans)
    defects=Counter(p['scenario']['data_quality_case_id'] for p in plans if p['scenario']['data_quality_case_id'])
    assert groups=={'coverage':175,'challenge':75} and len(defects)==6 and set(defects.values())=={5}
    assert not ({p['scenario']['id'] for p in plans} & {json.loads(x)['id'] for x in Path('scenarios/pilot_scenarios.jsonl').read_text().splitlines()})
    Path('scenarios/support_plans.jsonl').write_text(''.join(json.dumps(p,ensure_ascii=False)+'\n' for p in plans))
    print('Saved 250 independently grounded plans:',dict(groups),'and five cases for each of six defects.')


if __name__=='__main__':
    main()
