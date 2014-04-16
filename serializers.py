# -*- coding: utf-8 -*-
import re
import json

from resto.encoders import JSONEncoder


class JSONSerializer(object):
    content_type = "application/json"
    encoding = "UTF-8"

    def get_content_type(self):
        return "{}; charset={}".format(self.content_type, self.encoding)

    def serialize(self, data):
        return self.to_json(data)

    def to_json(self, data):
        return json.dumps(
            data, cls=JSONEncoder, sort_keys=True, ensure_ascii=False
        )


class CamelCaseJSONSerializer(JSONSerializer):
    def to_json(self, data, options=None):
        def underscoreToCamel(match):
            return match.group()[0] + match.group()[2].upper()

        def camelize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(
                        r"[a-z0-9]_[a-z]", underscoreToCamel, key
                    )
                    new_dict[new_key] = camelize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = camelize(data[i])
                return data
            return data

        camelized_data = camelize(data)

        return json.dumps(
            camelized_data, cls=JSONEncoder, sort_keys=True, ensure_ascii=False
        )

    def from_json(self, content):
        data = json.loads(content)

        def camelToUnderscore(match):
            return match.group()[0] + "_" + match.group()[1].lower()

        def underscorize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z0-9][A-Z]", camelToUnderscore, key)
                    new_dict[new_key] = underscorize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = underscorize(data[i])
                return data
            return data

        underscored_data = underscorize(data)

        return underscored_data
