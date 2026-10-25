cd "$(dirname "$0")/.."
l=$1; python3 driver/score.py runs/$l/out-$l > runs/$l/result.json && python3 -c "
import json;r=json.load(open('runs/$l/result.json'));s=r['sealed'];g=s['gates']
print('$l','gates',g['chain_ok'],g['control_ok'],g['split_classifier_caught'],'/',g['split_n'],g['compliant_labelled_bypass'],g['confess_final_flag'],'|',{k.split('/')[1]:(v['episodes'],v['scored'],v['D1'],v['D2'],v['D3'],v['D4']) for k,v in s['cells'].items()},r['h2_ext']['gate'],r['h2_ext']['fisher_one_sided_told_lt_untold'],'|',{k[:4]:(v['k'],v['n'],v['ci']) for k,v in s['false_alarm'].items()},{k:(v['k'],v['n'],v['ci']) for k,v in r['fa_strata_exploratory'].items()},r['per_task_final_msg_fa'])"
