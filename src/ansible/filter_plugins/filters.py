# Utility filters
from ansible.module_utils._text import to_text


class FilterModule(object):
    def filters(self):
        return {
            'remfromdict': self.rem_from_dict,
            'remfromlist': self.rem_from_list,
            'exprtype': self.expr_type,
            'splitsearch': self.split_search
        }

    def rem_from_dict(self, dict_, key):
        dict_.pop(to_text(key))

        return dict_

    def rem_from_list(self, list_, item):
        list_.remove(to_text(item))

        return list_

    
    def expr_type(self, expr):
        return to_text(type(expr).__name__)

    def split_search(self, to_search_in, delim, search_strs):
        res_strs = []
        for to_search_sub_str in to_search_in.split(delim):
            for search_str in search_strs:
                if search_str in to_search_sub_str:
                    res_strs.append(to_search_sub_str)

        return res_strs