import os
import shutil
import time
import re

from public_models.models import ParamInfo
from projectmanagement.models import ProjectSubstepFileInfo


def ismobile(phone):
    if phone == None or phone == '':
        return None
    ret = re.match(r"^1\d{10}$", phone)
    return ret


def move_project_file(project_code,step_code,substep_code,substep_serial):

    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value

    # 临时文件
    oldpath = '{}{}/{}/{}/{}/'.format(absolute_path, 'project', project_code, step_code,
                                      substep_code) + substep_serial + '/'
    # 正式文件
    newpath = '{}{}/{}/{}/{}/'.format(relative_path, 'project', project_code, step_code,
                                      substep_code) + substep_serial + '/'

    psfis = ProjectSubstepFileInfo.objects.filter(project_code=project_code, step_code=step_code,
                                                  substep_code=substep_code, substep_serial=substep_serial)
    if psfis != None and len(psfis) > 0:
        for psfi in psfis:
            # 修改表中数据
            psfi.state = 1
            psfi.save()

            # 移动附件
            filename = psfi['filename']

            # 将临时文件转为正式文件
            url_j_c = '{}{}'.format(oldpath, filename)
            if os.path.exists(url_j_c):

                # 更新绝对路径并转移文件
                url_x = newpath
                if not os.path.exists(url_x):
                    os.makedirs(url_x)
                url_x = url_x + filename
                shutil.move(url_j_c, url_x)

        # 所有文件移动完成后删除临时目录c
        os.rmdir(oldpath)







