# Simple optimizer wrapper using dimod simulated annealing (local)
from typing import Dict, Any, Tuple, List
import dimod
from dwave.samplers import SimulatedAnnealingSampler

BASE_VARS = {
    'P0': {'name':'Blueberries','weight':-0.05,'min':0,'max':200,'step':25,'unit':'mg'},
    'P1': {'name':'Broccoli','weight':-0.08,'min':0,'max':100,'step':20,'unit':'mg'},
    'N0': {'name':'Added sugars','weight':+0.10,'min':0,'max':50,'step':10,'unit':'g'},
    'E0': {'name':'Stress','weight':+0.15,'min':5,'max':30,'step':5,'unit':'µg/dL'},
    'C0': {'name':'Mindfulness','weight':-0.02,'min':0,'max':60,'step':15,'unit':'min'}
}

def apply_adjustments(vars_conf, adjustments):
    conf = {k:v.copy() for k,v in vars_conf.items()}
    for k,m in adjustments.items():
        if k in conf and 'weight_scale' in m:
            conf[k]['weight'] *= m['weight_scale']
    return conf

def build_bqm(vars_conf, days=2, slots=3, bits_per_var=3):
    bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, vartype=dimod.BINARY)
    bits_map = {}
    for day in range(days):
        for slot in range(slots):
            for vname, vinfo in vars_conf.items():
                bits = []
                for b in range(bits_per_var):
                    bit = f"{vname}_d{day}_s{slot}_b{b}"
                    bits.append(bit)
                    bqm.add_variable(bit, vinfo['weight'] * (2**b) * vinfo['step'])
                bits_map[(vname, day, slot)] = bits
                PEN = 1.8
                for i in range(len(bits)):
                    for j in range(i+1, len(bits)):
                        bqm.add_interaction(bits[i], bits[j], PEN)
    return bqm, bits_map

def solve_bqm(bqm, num_reads=200):
    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=num_reads)
    return sampleset.first

def run_qubo_plan(features: Dict[str,Any], days:int=2, user_id:str=None) -> Tuple[float, List[Dict[str,Any]]]:
    # features is dict of user features; use simple rule-based adjustments here
    adjustments = {}
    if features.get('bmi',0) > 28: adjustments['N0'] = {'weight_scale':1.5}
    if features.get('stress_score',0) > 6: adjustments['E0'] = {'weight_scale':1.3}
    vars_conf = apply_adjustments(BASE_VARS, adjustments)
    bqm, bits_map = build_bqm(vars_conf, days=days)
    best = solve_bqm(bqm, num_reads=200)
    sample = best.sample
    energy = best.energy
    plan = []
    for (vname, day, slot), bits in bits_map.items():
        level = sum((2**i) * sample[bits[i]] for i in range(len(bits)))
        value = vars_conf[vname]['min'] + level * vars_conf[vname]['step']
        value = min(value, vars_conf[vname]['max'])
        if value > vars_conf[vname]['min']:
            plan.append({
                'name': vars_conf[vname]['name'],
                'key': vname,
                'day': day+1,
                'slot': ['Morning','Afternoon','Evening'][slot],
                'value': value,
                'unit': vars_conf[vname]['unit']
            })
    return energy, plan
