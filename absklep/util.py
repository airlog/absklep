
def read_form(name, allow_none=False, cast=None):
    '''
    Odczytuje dane o zadanym kluczu 'name' z otrzymanego formularza. Jesli 'allow_none' jest równe False i wartosc
    odczytana z formularza bedzie None to wyrzuci wyjatek ValueError. Argument 'cast' powinien byc funkcja przyjmujaca
    jeden argument i zwracajaca wynik. Zostanie jej podana odczytana wartość.
    '''

    from flask import request

    tmp = request.form[name]

    if tmp is None and not allow_none:
        raise ValueError('None not allowed')

    if cast is None:
        return tmp
    else:
        return cast(tmp)
