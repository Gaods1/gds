import re
from rest_framework import serializers

class PatclubModelSerializer(serializers.ModelSerializer):
    @property
    def errors_message(self):
        _errors_message= {
            'required': self.required_errors_message,
            'null': self.null_errors_message,
            'unique': self.non_filed_errors_message,
            'invalid': self.invalid_errors_message,
        }
        return _errors_message

    @property
    def errors(self):
        if not hasattr(self, '_errors'):
            msg = 'You must call `.is_valid()` before accessing `.errors`.'
            raise AssertionError(msg)
        if self._errors:
            _translation_errors = []
            for key, values in self._errors.items():
                new_errors_message = []
                for v in values:
                    code = v.code
                    new_errors_message.append(self.errors_message[code](key, v))
                _translation_errors.extend(new_errors_message)
            translation_errors = '   '.join(_translation_errors)
            return {'detail': translation_errors}
        return self._errors

    def invalid_errors_message(self, key, value):
        return value

    def null_errors_message(self, key, value):
        f = self.fields[key].label
        return '【{}】不能为空值'.format(f)

    def required_errors_message(self, key, value):
        f = self.fields[key].label
        return '【{}】是必填项'.format(f)

    def non_filed_errors_message(self, key, value):
        r_unique_toger = "字段(.*?)必须能构成唯一集合。"
        r_unique = "具有 (.*?) 的 (.*?) 已存在。"
        results_unique = re.search(r_unique, value)
        results_unique_toger = re.search(r_unique_toger, value)
        if results_unique_toger:
            filed = results_unique_toger.group(1)
            fs = filed.replace(' ', '').split(',')
            fs_cn = []
            for f in fs:
                fs_cn .append(self.fields[f].label)
            return "具有当前【{}】的信息已存在".format(','.join(fs_cn))
        elif results_unique:
            m = results_unique.group(1)
            v = self.data[key]
            return "具有当前【{}: {}】的信息已存在。".format(m,v)
        else:
            return value