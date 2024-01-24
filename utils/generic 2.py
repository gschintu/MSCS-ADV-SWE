from collections import defaultdict

""" Generic Utils  """

class GenericUtils:
    """ Generic Utils """
    
    def __init__(self):
        return

    @staticmethod
    def datatables_extract_data_form(form):
        """
        :param form: MultiDict from `request.form`
        :return dict() list with data from request.form
            - return format:    {id1: {field1:val1, ...}, ...}
            - return type:      Strings    
        """

        # fill in id field automatically
        data = defaultdict(lambda: {})

        # fill in data[id][field] = value
        for formkey in form.keys():
            if formkey == 'action':
                continue

            datapart,idpart,fieldpart = formkey.split('[')

            if datapart != 'data':
                return f"invalid input in request: {formkey}", 400

            idvalue = int(idpart[0:-1])
            fieldname = fieldpart[0:-1]

            data[idvalue][fieldname] = form[formkey]

        return data