from collections import Counter, defaultdict
from statistics import mean


def outcome_index(data):
    cutoff = data['analysis_cutoff']
    indexed = {}
    for row in data['outcomes']:
        if row['observed_at'] > cutoff:
            continue
        learner = row['learner']
        if learner in indexed and indexed[learner] != row['result']:
            raise ValueError('同一学生有冲突的成绩记录：' + learner)
        indexed[learner] = row['result']
    return indexed


def assignment_index(data):
    indexed = {}
    classes = {row['class_id']: row for row in data['classes']}
    for row in data['assignments']:
        if row['class_id'] not in classes:
            raise ValueError('未登记的班级')
        if row['learner'] in indexed:
            raise ValueError('学生有重复分配')
        indexed[row['learner']] = {**row, 'lecture': classes[row['class_id']]['lecture']}
    return indexed


def baseline(data):
    assignments = assignment_index(data)
    outcomes = outcome_index(data)
    cells = defaultdict(list)
    for learner, row in assignments.items():
        if learner in outcomes:
            cells[(row['lecture'], row['practice'])].append(outcomes[learner])
    return {'classes': len(data['classes']), 'assigned': len(assignments),
            'observed': len(outcomes), 'kind': 'descriptive',
            'cells': [{'lecture': key[0], 'practice': key[1], 'n': len(values),
                       'mean': mean(values)} for key, values in sorted(cells.items())]}


def act(data, request):
    if request.get('operation') != 'contrast':
        raise ValueError('未知试验操作')
    component = request.get('component')
    if component not in ('lecture', 'practice'):
        raise ValueError('未知组件')
    groups = defaultdict(list)
    outcomes = outcome_index(data)
    for learner, row in assignment_index(data).items():
        if learner in outcomes:
            groups[row[component]].append(outcomes[learner])
    first, second = request['level_a'], request['level_b']
    if not groups[first] or not groups[second] or first == second:
        raise ValueError('需要两个不同且有记录的组件水平')
    return {'kind': 'raw_difference', 'component': component,
            'difference': mean(groups[first]) - mean(groups[second]),
            'counts': {first: len(groups[first]), second: len(groups[second])},
            'notice': '仅描述观测到的均值差，不作设计推断'}
