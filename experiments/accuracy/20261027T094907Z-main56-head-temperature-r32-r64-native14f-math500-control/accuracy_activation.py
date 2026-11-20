"""原105负载可不触发compute-order；不改变其负载或忽略显式拒绝。"""
import json
import activation_evidence as base


def capture(run,control,source,env):
    result=base.capture(run,control,source,env)
    stack=result['stack']
    records=stack['records']
    not_exercised=not records['compute_order_selected'] and not records['compute_order_rejected']
    q_installed=bool(records['q_fragment_install']) and all(
        item['value'].get('installed') is True for item in records['q_fragment_install'])
    normalized=result['normalization_install']
    normalized_ok=bool(normalized) and all(item['value'].get('installed') is True
        and item['value'].get('kernel_sha256')==base.EXPECTED_KERNEL for item in normalized)
    selected=result['selected_compiled_abi']
    prefill_ok=bool(q_installed and normalized_ok and selected and all(item['valid'] for item in selected)
        and result['graph_capture_log'] and not result['parse_errors'] and not stack['parse_errors']
        and stack['status']!='rejected')
    result['valid']=bool(result['stable_small_o']['valid'] and (result['valid'] or (not_exercised and prefill_ok)))
    result['compute_order_scope']='not_exercised' if not_exercised else 'observed_requires_valid_stack'
    result['accuracy_scope_note']='原105不改batch/采样；未触发compute-order不虚构选中，显式拒绝仍无效。同源码性能组承担compute-order实际门。'
    (control/'prefill-activation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
