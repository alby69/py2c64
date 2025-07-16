test_cases = [
    {
        "name": "Dizionario: Aggiunta e rimozione (V1)",
        "compiler_version": "V1",
        "code": "my_dict = {}\nmy_dict['c'] = 3\ndel my_dict['d']", # now there is a key error
        "expected": "data_structures/output_dict_add_remove.asm"
    },
    {
        "name": "Dizionario: Inizializzazione e accesso (V1)",
        "compiler_version": "V1",
        "code": "my_dict = {'a': 1, 'b': 2}\nx1 = my_dict['a']",
        "expected": "data_structures/output_dict_init_access.asm"
    },
    {
        "name": "Tuple (V1)",
        "compiler_version": "V1",
        "code": "t = (1, 2, 3)",
        "expected": "data_structures/output_tuple.asm",
    },
    {
        "name": "Set (V1)",
        "compiler_version": "V1",
        "code": "s = {1, 2, 3, 2, 1}",
        "expected": "data_structures/output_set.asm",
    },
]
