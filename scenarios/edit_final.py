"""Repair writer/critic drift while preserving plans and an explicit edit log.

These are editorial changes, not student assessments. They use only the saved
user brief; database facts and expected outcomes never supply user utterances.
"""
import json
from pathlib import Path
import re


def style_message(text, style, intent, brief, turn):
    text = text.strip()
    ending = '' if text.endswith(('.', '?', '!')) else '.'
    if style == 'requests_short_plain_answer':
        return text + ending + ' Keep it short and plain.'
    if style == 'frustrated_impatient':
        return text + ending + (' Please deal with this now.' if turn==0 else ' I need a clear answer.')
    if style == 'repetitive_pressuring':
        return text + ending + (' Please, I need a clear answer.' if turn==0 else ' I really need to understand this.')
    if style == 'confused_rambling':
        prefixes=["I'm getting a little lost here, and I'm not quite sure how to ask this. ","And I'm not sure about this part either. ","I'm still trying to work out what information is useful. "]
        return prefixes[turn%3] + text
    if style == 'typo_heavy':
        replacements={'please':'plese','Please':'Plese','could':'coud','Could':'Coud',
                      'Can':'Cn','can':'cn','you':'yu','the':'teh',
                      'check':'chek','refund':'refnd','process':'proces','where':'wher',
                      'Where':'Wher','would':'woud','customer':'custmer','change':'chnge',
                      'information':'informtion','What':'Wht','what':'wht','help':'hlep'}
        for word, replacement in replacements.items():
            text=re.sub(r'\b'+word+r'\b',replacement,text)
        return text
    if style in {'terse_fragmentary','operational_shorthand'}:
        subject='my order' if brief['role']=='shopper' else 'store order' if brief['role']=='merchant' else 'customer order'
        if turn==0 and intent in {'refund','cancellation'} and '{{ORDER}}' in text:
            amount='{{AMOUNT}} refund' if '{{AMOUNT}}' in text else 'Full refund' if intent=='refund' else 'Cancel'
            return f'{amount}: {subject} {{{{ORDER}}}}. No longer wanted.'
        if turn==0 and intent=='order_lookup' and '{{ORDER}}' in text and not any(w in text.casefold() for w in ['date','product','seller','store details','timeline','sequence','shipping','shipment','delivery']):
            return f'{subject.capitalize()} {{{{ORDER}}}}: status?'
        text=re.sub(r'^(?:Could you |Can you |Please |please |I need you to )','',text)
        return text[0].upper()+text[1:]
    return text


def main():
    path=Path('scenarios/support_scenarios.jsonl')
    scenarios=[json.loads(x) for x in path.read_text().splitlines()]
    plans={p['scenario']['id']:p for p in map(json.loads,Path('scenarios/support_plans.jsonl').read_text().splitlines())}
    edits={}
    signatures=set()
    for scenario in scenarios:
        plan=plans[scenario['id']]; brief=plan['user_brief']; intent=scenario['tuple']['intent']; style=brief['user_style']
        scenario['extra_metadata']=plan['grounding']
        # Work on the unbound model output; bind only after editorial changes.
        audit=json.loads(Path(f"scenarios/results/hw3/final-generation/{scenario['id']}-critic.json").read_text())
        original=audit['conversation']; messages=[original['opening_message'],*original['followups']]
        opening=messages[0]; joined=' '.join(messages); seed=brief['draft_messages'][0]
        reasons=[]
        if re.search(r'\b(?:cw-[a-z]|get_order|search_products|issue_refund|cancel_order|scenario_id|trace|prompt)\b',joined,re.I):
            reasons.append('remove internal implementation terminology')
        if brief['role']!='shopper' and re.search(r'\bmy order\b|\bI ordered\b',opening,re.I) and not re.search(r'\bmy order\b|\bI ordered\b',seed,re.I):
            reasons.append('restore the authenticated user role')
        if intent=='refund' and not re.search(r'\brefund\b|money back',opening,re.I):
            reasons.append('restore the explicit refund request')
        if intent=='cancellation' and not re.search(r'cancel',opening,re.I):
            reasons.append('restore cancellation intent')
        if intent=='product_search' and re.search(r'\bmy order\b|\bI ordered\b|\brefund\b',opening,re.I):
            reasons.append('restore product search rather than order/refund intent')
        if intent=='product_search':
            product=brief['user_visible_facts'].get('product','Portable Tray')
            if not all(word.casefold() in opening.casefold() for word in product.split()):
                reasons.append('restore the supplied product name or description')
            if not brief['user_visible_facts'].get('product') and not re.search(r'actual.*(?:name|title)|(?:name|title).*(?:shown|display|listing)|read.*name',opening,re.I):
                reasons.append('restore the request for the actual displayed title')
        if intent=='policy_question':
            for term in ['payout','return','refund','shipping','ship','restocking','dispute','cancel']:
                if term in seed.casefold() and term not in opening.casefold():
                    reasons.append('restore the planned policy topic'); break
            if ('when' in seed.casefold() or 'how long' in seed.casefold()) and not re.search(r'when|how long|time|start|duration',opening,re.I):
                reasons.append('restore the planned timing question')
        if intent=='out_of_scope':
            topic_patterns = [
                (r'legal|lease|contract',r'legal|lease|contract|rental'),
                (r'investment|savings',r'invest|savings|financial'),
                (r'flight',r'flight|airline|travel'),
                (r'router|Wi-Fi',r'router|Wi-Fi|network'),
                (r'card|payment credentials',r'card|payment|credentials'),
                (r'mobile phone company',r'phone company|mobile|phone bill'),
            ]
            for seed_pattern, request_pattern in topic_patterns:
                if re.search(seed_pattern,seed,re.I) and not re.search(request_pattern,opening,re.I):
                    reasons.append('restore the out-of-scope topic rather than an invented Cartwheel issue')
            if 'mobile phone company' in seed and not re.search(r'company|carrier|provider',opening,re.I):
                reasons.append('identify that the billing dispute is with another company')
        if intent=='order_lookup' and scenario.get('data_quality_case_id')=='dq-order-reversed-dates' and not re.search(r'date|timeline|sequence|shipping|delivery|shipment',opening,re.I):
            reasons.append('restore the requested shipment/delivery chronology')
        if intent=='order_lookup' and scenario.get('data_quality_case_id')=='dq-order-store-mismatch' and not re.search(r'product|seller|store details|purchased item',opening,re.I):
            reasons.append('restore the product/seller consistency question')
        if '{{OTHER_ORDER}}' in brief.get('allowed_placeholders',[]) and '{{OTHER_ORDER}}' not in messages[1]:
            reasons.append('preserve the order correction in the second turn')
        if 'friend' in seed and 'friend' not in opening.casefold():
            reasons.append('keep the shared-receipt authorization edge explicit')
        if 'another merchant' in seed and not re.search(r'another|other merchant',opening,re.I):
            reasons.append('keep the other-store authorization edge explicit')
        if re.search(r"already (?:contacted|requested|returned|refunded)|haven't received|have not received|never arrived|was cancelled|last week|it's been|supposed to receive|technical issue",joined,re.I):
            reasons.append('remove invented order history or prior actions')
        if any(re.match(r'\s*(?:yes\b|thank you for|thanks for|go ahead\b)',m,re.I) for m in messages[1:]):
            reasons.append('remove followups that assume a particular agent reply')
        if reasons:
            messages=list(brief['draft_messages'])
        for index,message in enumerate(messages):
            needs_style=False
            if style=='requests_short_plain_answer': needs_style=not re.search(r'short|plain|simple|brief',message,re.I)
            elif style=='frustrated_impatient': needs_style=not re.search(r'ASAP|urgent|now|frustrat|already|hurry',message,re.I)
            elif style=='repetitive_pressuring': needs_style=not re.search(r'really|must|need.*need|please.*please|urgent',message,re.I)
            elif style=='confused_rambling': needs_style=not re.search(r'confus|not sure|unsure|lost|think|trying',message,re.I)
            elif style in {'terse_fragmentary','operational_shorthand'}: needs_style=bool(re.match(r'Could you|Can you|Please|I would',message)) or len(message.split())>22
            elif style=='typo_heavy': needs_style=not re.search(r'chek|refnd|proces\b|plese|coud|woud|custmer|informtion|recie|becuse|dont|whats|figger|diferent|dose',message,re.I)
            if needs_style or reasons:
                messages[index]=style_message(message,style,intent,brief,index)
                if needs_style: reasons.append('preserve the assigned language style')
        bound=messages
        for token,value in plan['bindings'].items(): bound=[s.replace(token,value) for s in bound]
        signature=tuple(s.strip().casefold() for s in bound)
        if signature in signatures:
            # Keep the real goal, not a numbering tag or irrelevant invented fact.
            options=['Please explain the next step.', 'I would like a clear answer on this.', 'Please address the specific question.']
            for extra in options:
                bound[0]=bound[0].rstrip('.')+'. '+extra
                signature=tuple(s.strip().casefold() for s in bound)
                if signature not in signatures: break
            reasons.append('remove a duplicate conversation')
        assert signature not in signatures and len(bound)==scenario['tuple']['turn_count']
        assert all('{{' not in s for s in bound)
        signatures.add(signature)
        after={'opening_message':bound[0],'followups':bound[1:]}
        raw_bound=[original['opening_message'],*original['followups']]
        for token,value in plan['bindings'].items(): raw_bound=[s.replace(token,value) for s in raw_bound]
        before={'opening_message':raw_bound[0],'followups':raw_bound[1:]}
        if before!=after:
            edits[scenario['id']]={'reason':'; '.join(dict.fromkeys(reasons)), 'before':before,'after':after}
            scenario.update(after)
    human_review=Path('scenarios/support_review.jsonl')
    if human_review.exists():
        by_id={s['id']:s for s in scenarios}
        for line in human_review.read_text().splitlines():
            decision=json.loads(line)
            if decision['decision']=='revise' and decision['change']:
                scenario=by_id[decision['scenario_id']]
                before={k:scenario[k] for k in ['opening_message','followups']}
                scenario.update(decision['change'])
                prior=edits.get(scenario['id'])
                edits[scenario['id']]={
                    'reason':(prior['reason']+'; ' if prior else '')+'student-approved final review: '+decision['reason'],
                    'before':prior['before'] if prior else before,
                    'after':{k:scenario[k] for k in before},
                }
    path.write_text(''.join(json.dumps(s,ensure_ascii=False)+'\n' for s in scenarios))
    Path('scenarios/support_edits.json').write_text(json.dumps(edits,indent=2,ensure_ascii=False)+'\n')
    print(f'Saved {len(edits)} transparent conversation edits; preserved grounded plans and raw independent writer/critic calls.')


if __name__=='__main__': main()
