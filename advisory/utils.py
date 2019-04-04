from achievement.models import *
from expert.models import *
from projectmanagement.models import *


def get_r_code(code):
    return ResultsInfo.objects.get(r_code=code).serial


def get_req_code(code):
    return RequirementsInfo.objects.get(req_code=code).serial


def get_project_code(code):
    return ProjectInfo.objects.get(project_code=code).serial


def get_expert_code(code):
    return ExpertBaseinfo.objects.get(expert_code=code).serial


def get_broker_code(code):
    return BrokerBaseinfo.objects.get(broker_code=code).serial


def get_pt_code(code):
    return ProjectTeamBaseinfo.objects.get(pt_code=code).serial


def get_collector_code(code):
    return CollectorBaseinfo.objects.get(collector_code=code).serial


def get_other(code):
    return None

type_model = {
    1: get_r_code,
    2: get_req_code,
    3: get_project_code,
    5: get_expert_code,
    6: get_broker_code,
    7: get_pt_code,
    8: get_collector_code,
    9: get_other
}


type_index = {
    1: 'result_detail',
    2: 'requirement_detail',
    3: 'project_detail',
    5: 'expert_detail',
    6: 'broker_detail',
    7: 'team_detail',
    8: 'collector_detail',
}