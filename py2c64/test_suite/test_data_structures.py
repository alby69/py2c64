test_cases = [
    {
        "name": "Dizionario: Aggiunta e rimozione",
        "code": "my_dict = {}\nmy_dict['c'] = 3\ndel my_dict['d']", # now there is a key error
        "expected": "data_structures/output_dict_add_remove.asm"
    },
    {
        "name": "Dizionario: Inizializzazione e accesso",
        "code": "my_dict = {'a': 1, 'b': 2}\nx1 = my_dict['a']",
        "expected": "data_structures/output_dict_init_access.asm"
    },
    {
        "name": "Tuple",
        "code": "t = (1, 2, 3)",
        "expected": "data_structures/output_tuple.asm",
    },
    {
        "name": "Set",
        "code": "s = {1, 2, 3, 2, 1}",
        "expected": "data_structures/output_set.asm",
    },
]
