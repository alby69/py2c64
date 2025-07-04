# py2asm/lib/ast_processor.py
import ast
from .. import globals
from . import func_expressions
from . import func_core
from . import func_dict

# Aliases
gen_code = globals.generated_code
variables = globals.variables
used_routines = globals.used_routines
report_error = globals.report_compiler_error

# NOTA: Si assume che esista una funzione `func_expressions.process_expression`
# che valuta un'espressione e lascia il risultato a 16 bit nei registri A/X.
# Questa è un'astrazione necessaria per concentrarsi sulla logica di chiamata.
def _evaluate_expression_to_ax(node, error_handler_func, current_func_info=None):
    """
    Wrapper per la logica di valutazione delle espressioni.
    Genera codice che lascia un risultato a 16 bit in A (high byte) e X (low byte).
    """
    # La vera logica è delegata ad altri moduli come func_expressions.py
    temp_result_var = func_core.get_temp_var()
    func_expressions.translate_expression_recursive(temp_result_var, node, current_func_info.get('name') if current_func_info else None)

    is_float_result = variables.get(temp_result_var, {}).get('type') == 'float'

    if is_float_result:
        # Convert float to int for pushing onto the 16-bit stack.
        # This is a temporary simplification. Proper float argument handling is needed.
        gen_code.extend(func_core._generate_float_to_int_conversion(temp_result_var, temp_result_var)) # type: ignore
        # Now temp_result_var holds the 16-bit integer representation.
        gen_code.append(f"    LDA {temp_result_var}+1") # High byte
        gen_code.append(f"    LDX {temp_result_var}")   # Low byte
    else:
        gen_code.append(f"    LDA {temp_result_var}+1") # High byte
        gen_code.append(f"    LDX {temp_result_var}")   # Low byte

    func_core.release_temp_var(temp_result_var)


def _get_mangled_local_var_name(func_name, var_name):
    """Mangles a local variable name with its function scope."""
    return f"__{func_name}_{var_name}"

def process_expr_node(node, error_handler_func, current_func_info=None):
    """Processes an ast.Expr node, which is a wrapper for standalone expressions like function calls."""
    if not isinstance(node, ast.Expr):
        return

    if isinstance(node.value, ast.Call):
        call_node = node.value
        if not isinstance(call_node.func, ast.Name):
            report_error("Calling methods on objects is not supported.", node=call_node)
            return

        func_name = call_node.func.id

        # --- Gestione funzioni built-in (logica esistente, non modificata) ---
        # --- Gestione draw_line (caso speciale con passaggio parametri in Zero-Page) ---
        if func_name == 'draw_line':
            if len(call_node.args) != 4:
                report_error(f"Function 'draw_line' expects 4 arguments, got {len(call_node.args)}.", node=call_node)
                return

            # Definizioni delle locazioni Zero-Page e dei tipi di argomento
            zp_bases = [0xB0, 0xB2, 0xB6, 0xB8]
            is_16bit = [True, False, True, False]

            gen_code.append(f"    ; --- Preparazione chiamata a draw_line ---")
            for i, arg_node in enumerate(call_node.args):
                # Valuta l'espressione dell'argomento in una variabile temporanea
                temp_arg_var = func_core.get_temp_var()
                func_expressions.translate_expression_recursive(temp_arg_var, arg_node, current_func_info.get('name') if current_func_info else None)

                zp_addr = zp_bases[i]
                # Genera codice per spostare il valore dalla variabile temporanea alla locazione ZP
                if is_16bit[i]:
                    # Argomento a 16 bit (x1, x2)
                    gen_code.append(f"    LDA {temp_arg_var}      ; LSB")
                    gen_code.append(f"    STA ${zp_addr:02X}")
                    gen_code.append(f"    LDA {temp_arg_var}+1    ; MSB")
                    gen_code.append(f"    STA ${zp_addr+1:02X}")
                else:
                    # Argomento a 8 bit (y1, y2)
                    gen_code.append(f"    LDA {temp_arg_var}      ; LSB è sufficiente")
                    gen_code.append(f"    STA ${zp_addr:02X}")

                func_core.release_temp_var(temp_arg_var)

            # Chiama la routine e aggiungila al set di quelle usate
            gen_code.append("    JSR gfx_draw_line")
            used_routines.add('gfx_draw_line')
            gen_code.append(f"    ; --- Fine chiamata a draw_line ---")
            return # Chiamata gestita

        # --- NEW: Handle gfx_turn_on, gfx_turn_off, gfx_clear_screen ---
        if func_name in ['gfx_turn_on', 'gfx_turn_off', 'gfx_clear_screen']:
            if len(call_node.args) != 0:
                report_error(f"Function '{func_name}' expects 0 arguments, got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    JSR {func_name}")
            used_routines.add(func_name)
            return

        # --- Gestione draw_ellipse (caso speciale con passaggio parametri in Zero-Page) ---
        if func_name == 'draw_ellipse':
            if len(call_node.args) != 4:
                report_error(f"Function 'draw_ellipse' expects 4 arguments (xm, ym, xr, yr), got {len(call_node.args)}.", node=call_node)
                return

            # Definizioni delle locazioni Zero-Page e dei tipi di argomento
            # xm, ym (centro), xr, yr (raggi)
            zp_bases = [0xB0, 0xB2, 0xB6, 0xB8] # xm(16), ym(8), xr(16), yr(8)
            is_16bit = [True, False, True, False]

            gen_code.append(f"    ; --- Preparazione chiamata a draw_ellipse ---")
            for i, arg_node in enumerate(call_node.args):
                temp_arg_var = func_core.get_temp_var()
                func_expressions.translate_expression_recursive(temp_arg_var, arg_node, current_func_info.get('name') if current_func_info else None)

                zp_addr = zp_bases[i]
                if is_16bit[i]:
                    # Argomento a 16 bit (xm, xr)
                    gen_code.append(f"    LDA {temp_arg_var}      ; LSB")
                    gen_code.append(f"    STA ${zp_addr:02X}")
                    gen_code.append(f"    LDA {temp_arg_var}+1    ; MSB")
                    gen_code.append(f"    STA ${zp_addr+1:02X}")
                else:
                    # Argomento a 8 bit (ym, yr)
                    gen_code.append(f"    LDA {temp_arg_var}      ; LSB è sufficiente")
                    gen_code.append(f"    STA ${zp_addr:02X}")

                func_core.release_temp_var(temp_arg_var)

            gen_code.append("    JSR gfx_draw_ellipse")
            used_routines.add('gfx_draw_ellipse')
            gen_code.append(f"    ; --- Fine chiamata a draw_ellipse ---")
            return # Chiamata gestita

        # --- Gestione draw_circle (caso speciale, usa la routine di draw_ellipse) ---
        if func_name == 'draw_circle':
            if len(call_node.args) != 3:
                report_error(f"Function 'draw_circle' expects 3 arguments (x, y, radius), got {len(call_node.args)}.", node=call_node)
                return

            # Argomenti: x (16bit), y (8bit), r (usato per xr e yr)
            # Locazioni ZP: xm(0xB0, 16b), ym(0xB2, 8b), xr(0xB6, 16b), yr(0xB8, 8b)
            zp_map = {
                0: {'zp_base': 0xB0, 'is_16bit': True},  # x -> xm
                1: {'zp_base': 0xB2, 'is_16bit': False}, # y -> ym
                2: {'zp_base': 0xB6, 'is_16bit': True},  # r -> xr
            }

            gen_code.append(f"    ; --- Preparazione chiamata a draw_circle (via draw_ellipse) ---")

            # Valuta i 3 argomenti (x, y, r) e li mette nelle ZP per xm, ym, xr
            for i, arg_node in enumerate(call_node.args):
                temp_arg_var = func_core.get_temp_var()
                func_expressions.translate_expression_recursive(temp_arg_var, arg_node, current_func_info.get('name') if current_func_info else None)

                zp_addr = zp_map[i]['zp_base']
                if zp_map[i]['is_16bit']:
                    gen_code.append(f"    LDA {temp_arg_var}      ; LSB")
                    gen_code.append(f"    STA ${zp_addr:02X}")
                    gen_code.append(f"    LDA {temp_arg_var}+1    ; MSB")
                    gen_code.append(f"    STA ${zp_addr+1:02X}")
                else:
                    gen_code.append(f"    LDA {temp_arg_var}      ; LSB è sufficiente")
                    gen_code.append(f"    STA ${zp_addr:02X}")

                # Se stiamo processando il raggio (argomento 2), copialo anche in yr (0xB8)
                if i == 2:
                    gen_code.append(f"    ; Copia raggio (LSB) in ZP per yr")
                    gen_code.append(f"    LDA {temp_arg_var}      ; LSB del raggio")
                    gen_code.append(f"    STA ${0xB8:02X}         ; Salva in yr (8-bit)") # type: ignore

                func_core.release_temp_var(temp_arg_var)

            gen_code.append("    JSR gfx_draw_ellipse")
            used_routines.add('gfx_draw_ellipse')
            gen_code.append(f"    ; --- Fine chiamata a draw_circle ---")
            return # Chiamata gestita

        # --- Gestione draw_rect (caso speciale con passaggio parametri in Zero-Page) ---
        if func_name == 'draw_rect':
            if len(call_node.args) != 4:
                report_error(f"Function 'draw_rect' expects 4 arguments (x1, y1, x2, y2), got {len(call_node.args)}.", node=call_node)
                return

            # Definizioni delle locazioni Zero-Page e dei tipi di argomento
            zp_bases = [0xB0, 0xB2, 0xB6, 0xB8] # x1(16), y1(8), x2(16), y2(8)
            is_16bit = [True, False, True, False]

            gen_code.append(f"    ; --- Preparazione chiamata a draw_rect ---")
            for i, arg_node in enumerate(call_node.args):
                temp_arg_var = func_core.get_temp_var()
                func_expressions.translate_expression_recursive(temp_arg_var, arg_node, current_func_info.get('name') if current_func_info else None)

                zp_addr = zp_bases[i]
                if is_16bit[i]:
                    gen_code.append(f"    LDA {temp_arg_var}; STA ${zp_addr:02X}")
                    gen_code.append(f"    LDA {temp_arg_var}+1; STA ${zp_addr+1:02X}")
                else:
                    gen_code.append(f"    LDA {temp_arg_var}; STA ${zp_addr:02X}")
                func_core.release_temp_var(temp_arg_var)

            gen_code.append("    JSR gfx_draw_rect")
            used_routines.add('gfx_draw_rect')
            gen_code.append(f"    ; --- Fine chiamata a draw_rect ---")
            return # Chiamata gestita

        # --- NEW: Gestione Funzioni Sprite ---

        if func_name == 'sprite_set_pos':
            if len(call_node.args) != 3:
                report_error(f"Function 'sprite_set_pos' expects 3 arguments (num, x, y), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_pos ---")

            # Arguments are: num, x, y
            arg_num_node = call_node.args[0]
            arg_x_node = call_node.args[1]
            arg_y_node = call_node.args[2]

            # Evaluate arguments into temporary variables first to avoid register clobbering
            temp_num = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_num, arg_num_node, current_func_info.get('name') if current_func_info else None)

            temp_x = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_x, arg_x_node, current_func_info.get('name') if current_func_info else None)

            temp_y = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_y, arg_y_node, current_func_info.get('name') if current_func_info else None)

            # Now, load the values into the correct registers/ZP locations
            # Store X coordinate in $B0 (used by the routine)
            gen_code.append(f"    LDA {temp_x}      ; Carica LSB della coordinata X")
            gen_code.append(f"    STA $B0")

            # Load sprite number into X register
            gen_code.append(f"    LDX {temp_num}      ; Carica numero sprite in X")

            # Load Y coordinate into A register
            gen_code.append(f"    LDA {temp_y}      ; Carica coordinata Y in A")

            # Call the routine
            gen_code.append("    JSR sprite_set_pos")
            used_routines.add('sprite_set_pos')

            gen_code.append(f"    ; --- Fine chiamata a sprite_set_pos ---")
            return # Chiamata gestita

        if func_name == 'sprite_set_color':
            if len(call_node.args) != 2:
                report_error(f"Function 'sprite_set_color' expects 2 arguments (num, color), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_color ---")

            arg_num_node = call_node.args[0]
            arg_color_node = call_node.args[1]

            # Evaluate arguments into temporary variables
            temp_num = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_num, arg_num_node, current_func_info.get('name') if current_func_info else None)

            temp_color = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_color, arg_color_node, current_func_info.get('name') if current_func_info else None)

            # Load sprite number into X register
            gen_code.append(f"    LDX {temp_num}      ; Carica numero sprite in X")

            # Load color into A register
            gen_code.append(f"    LDA {temp_color}      ; Carica colore in A")

            # Call the routine
            gen_code.append("    JSR sprite_set_color")
            used_routines.add('sprite_set_color')

            gen_code.append(f"    ; --- Fine chiamata a sprite_set_color ---")
            func_core.release_temp_var(temp_num)
            func_core.release_temp_var(temp_color)
            return # Chiamata gestita

        if func_name == 'sprite_enable':
            if len(call_node.args) != 1:
                report_error(f"Function 'sprite_enable' expects 1 argument (mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_enable ---")
            arg_mask_node = call_node.args[0]
            temp_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mask, arg_mask_node, current_func_info.get('name') if current_func_info else None)
            gen_code.append(f"    LDA {temp_mask}      ; Carica maschera in A")
            gen_code.append("    JSR sprite_enable")
            used_routines.add('sprite_enable')
            gen_code.append(f"    ; --- Fine chiamata a sprite_enable ---")
            func_core.release_temp_var(temp_mask)
            return # Chiamata gestita

        if func_name == 'sprite_disable':
            if len(call_node.args) != 1:
                report_error(f"Function 'sprite_disable' expects 1 argument (mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_disable ---")
            arg_mask_node = call_node.args[0]
            temp_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mask, arg_mask_node, current_func_info.get('name') if current_func_info else None)
            gen_code.append(f"    LDA {temp_mask}      ; Carica maschera in A")
            gen_code.append("    JSR sprite_disable")
            used_routines.add('sprite_disable')
            gen_code.append(f"    ; --- Fine chiamata a sprite_disable ---")
            func_core.release_temp_var(temp_mask)
            return # Chiamata gestita

        if func_name == 'sprite_set_x_msb':
            if len(call_node.args) != 1:
                report_error(f"Function 'sprite_set_x_msb' expects 1 argument (mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_x_msb ---")
            arg_mask_node = call_node.args[0]
            temp_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mask, arg_mask_node, current_func_info.get('name') if current_func_info else None)
            gen_code.append(f"    LDA {temp_mask}      ; Carica maschera in A")
            gen_code.append("    JSR sprite_set_x_msb")
            used_routines.add('sprite_set_x_msb')
            gen_code.append(f"    ; --- Fine chiamata a sprite_set_x_msb ---")
            func_core.release_temp_var(temp_mask)
            return # Chiamata gestita

        if func_name == 'sprite_set_x_msb_clear':
            if len(call_node.args) != 1:
                report_error(f"Function 'sprite_set_x_msb_clear' expects 1 argument (mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_x_msb_clear ---")
            arg_mask_node = call_node.args[0]
            temp_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mask, arg_mask_node, current_func_info.get('name') if current_func_info else None)
            gen_code.append(f"    LDA {temp_mask}      ; Carica maschera in A")
            gen_code.append("    JSR sprite_set_x_msb_clear")
            used_routines.add('sprite_set_x_msb_clear')
            gen_code.append(f"    ; --- Fine chiamata a sprite_set_x_msb_clear ---")
            func_core.release_temp_var(temp_mask)
            return # Chiamata gestita

        if func_name == 'sprite_expand_xy':
            if len(call_node.args) != 2:
                report_error(f"Function 'sprite_expand_xy' expects 2 arguments (y_mask, x_mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_expand_xy ---")

            arg_y_mask_node = call_node.args[0]
            arg_x_mask_node = call_node.args[1]

            # Evaluate arguments into temporary variables first
            temp_y_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_y_mask, arg_y_mask_node, current_func_info.get('name') if current_func_info else None)

            temp_x_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_x_mask, arg_x_mask_node, current_func_info.get('name') if current_func_info else None)

            # Load x_mask into X register
            gen_code.append(f"    LDX {temp_x_mask}      ; Carica x_mask in X")

            # Load y_mask into A register
            gen_code.append(f"    LDA {temp_y_mask}      ; Carica y_mask in A")

            # Call the routine
            gen_code.append("    JSR sprite_expand_xy")
            used_routines.add('sprite_expand_xy')

            gen_code.append(f"    ; --- Fine chiamata a sprite_expand_xy ---")
            func_core.release_temp_var(temp_y_mask)
            func_core.release_temp_var(temp_x_mask)
            return # Chiamata gestita

        if func_name == 'sprite_set_pointer':
            if len(call_node.args) != 2:
                report_error(f"Function 'sprite_set_pointer' expects 2 arguments (num, pointer_val), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_pointer ---")

            arg_num_node = call_node.args[0]
            arg_ptr_node = call_node.args[1]

            # Evaluate arguments into temporary variables
            temp_num = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_num, arg_num_node, current_func_info.get('name') if current_func_info else None)

            temp_ptr = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_ptr, arg_ptr_node, current_func_info.get('name') if current_func_info else None)

            # Load sprite number into X register
            gen_code.append(f"    LDX {temp_num}      ; Carica numero sprite in X")

            # Load pointer value into A register
            gen_code.append(f"    LDA {temp_ptr}      ; Carica valore puntatore in A")

            # Call the routine
            gen_code.append("    JSR sprite_set_pointer")
            used_routines.add('sprite_set_pointer')

            gen_code.append(f"    ; --- Fine chiamata a sprite_set_pointer ---")
            func_core.release_temp_var(temp_num)
            func_core.release_temp_var(temp_ptr)
            return # Chiamata gestita

        if func_name == 'sprite_set_priority':
            if len(call_node.args) != 1:
                report_error(f"Function 'sprite_set_priority' expects 1 argument (mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_priority ---")
            arg_mask_node = call_node.args[0]
            temp_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mask, arg_mask_node, current_func_info.get('name') if current_func_info else None)
            gen_code.append(f"    LDA {temp_mask}      ; Carica maschera in A")
            gen_code.append("    JSR sprite_set_priority")
            used_routines.add('sprite_set_priority')
            gen_code.append(f"    ; --- Fine chiamata a sprite_set_priority ---")
            func_core.release_temp_var(temp_mask)
            return # Chiamata gestita

        if func_name == 'sprite_set_multicolor':
            if len(call_node.args) != 1:
                report_error(f"Function 'sprite_set_multicolor' expects 1 argument (mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_multicolor ---")
            arg_mask_node = call_node.args[0]
            temp_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mask, arg_mask_node, current_func_info.get('name') if current_func_info else None)
            gen_code.append(f"    LDA {temp_mask}      ; Carica maschera in A")
            gen_code.append("    JSR sprite_set_multicolor")
            used_routines.add('sprite_set_multicolor')
            gen_code.append(f"    ; --- Fine chiamata a sprite_set_multicolor ---")
            func_core.release_temp_var(temp_mask)
            return # Chiamata gestita

        if func_name == 'sprite_set_multicolor_colors':
            if len(call_node.args) != 2:
                report_error(f"Function 'sprite_set_multicolor_colors' expects 2 arguments (mc1, mc2), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_multicolor_colors ---")

            arg_mc1_node = call_node.args[0]
            arg_mc2_node = call_node.args[1]

            # Evaluate arguments into temporary variables first
            temp_mc1 = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mc1, arg_mc1_node, current_func_info.get('name') if current_func_info else None)

            temp_mc2 = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mc2, arg_mc2_node, current_func_info.get('name') if current_func_info else None)

            # Load mc2 into X register
            gen_code.append(f"    LDX {temp_mc2}      ; Carica mc2 in X")

            # Load mc1 into A register
            gen_code.append(f"    LDA {temp_mc1}      ; Carica mc1 in A")

            # Call the routine
            gen_code.append("    JSR sprite_set_multicolor_colors")
            used_routines.add('sprite_set_multicolor_colors')

            gen_code.append(f"    ; --- Fine chiamata a sprite_set_multicolor_colors ---")
            func_core.release_temp_var(temp_mc1)
            func_core.release_temp_var(temp_mc2)
            return # Chiamata gestita

        if func_name == 'sprite_create_from_data':
            if len(call_node.args) != 2:
                report_error(f"Function 'sprite_create_from_data' expects 2 arguments (sprite_num, source_addr), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_create_from_data ---")

            arg_num_node = call_node.args[0]
            arg_addr_node = call_node.args[1]

            # Evaluate arguments into temporary variables first
            temp_num = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_num, arg_num_node, current_func_info.get('name') if current_func_info else None)

            temp_addr = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_addr, arg_addr_node, current_func_info.get('name') if current_func_info else None)

            # Load source_addr into ZP pointer $F0/$F1 (ZP_SRC_PTR in the routine)
            gen_code.append(f"    LDA {temp_addr}      ; Carica LSB dell'indirizzo sorgente")
            gen_code.append(f"    STA $F0")
            gen_code.append(f"    LDA {temp_addr}+1    ; Carica MSB dell'indirizzo sorgente")
            gen_code.append(f"    STA $F1")

            # Load sprite number into X register
            gen_code.append(f"    LDX {temp_num}      ; Carica numero sprite in X")

            # Call the routine
            gen_code.append("    JSR sprite_create_from_data")
            used_routines.add('sprite_create_from_data')

            gen_code.append(f"    ; --- Fine chiamata a sprite_create_from_data ---")
            func_core.release_temp_var(temp_num)
            func_core.release_temp_var(temp_addr)
            return # Chiamata gestita

        if func_name == 'sprite_set_priority':
            if len(call_node.args) != 1:
                report_error(f"Function 'sprite_set_priority' expects 1 argument (mask), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_priority ---")
            arg_mask_node = call_node.args[0]
            temp_mask = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_mask, arg_mask_node, current_func_info.get('name') if current_func_info else None)
            gen_code.append(f"    LDA {temp_mask}      ; Carica maschera in A")
            gen_code.append("    JSR sprite_set_priority")
            used_routines.add('sprite_set_priority')
            gen_code.append(f"    ; --- Fine chiamata a sprite_set_priority ---")
            func_core.release_temp_var(temp_mask)
            return # Chiamata gestita

        if func_name == 'sprite_create_from_data':
            if len(call_node.args) != 2:
                report_error(f"Function 'sprite_create_from_data' expects 2 arguments (sprite_num, source_addr), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_create_from_data ---")

            arg_num_node = call_node.args[0]
            arg_addr_node = call_node.args[1]

            # Evaluate arguments into temporary variables first
            temp_num = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_num, arg_num_node, current_func_info.get('name') if current_func_info else None)

            temp_addr = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_addr, arg_addr_node, current_func_info.get('name') if current_func_info else None)

            # Load source_addr into ZP pointer $F0/$F1 (ZP_SRC_PTR in the routine)
            gen_code.append(f"    LDA {temp_addr}      ; Carica LSB dell'indirizzo sorgente")
            gen_code.append(f"    STA $F0")
            gen_code.append(f"    LDA {temp_addr}+1    ; Carica MSB dell'indirizzo sorgente")
            gen_code.append(f"    STA $F1")

            # Load sprite number into X register
            gen_code.append(f"    LDX {temp_num}      ; Carica numero sprite in X")

            # Call the routine
            gen_code.append("    JSR sprite_create_from_data")
            used_routines.add('sprite_create_from_data')

            gen_code.append(f"    ; --- Fine chiamata a sprite_create_from_data ---")
            func_core.release_temp_var(temp_num)
            func_core.release_temp_var(temp_addr)
            return # Chiamata gestita

        if func_name == 'sprite_set_pointer':
            if len(call_node.args) != 2:
                report_error(f"Function 'sprite_set_pointer' expects 2 arguments (num, pointer_val), got {len(call_node.args)}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a sprite_set_pointer ---")

            arg_num_node = call_node.args[0]
            arg_ptr_node = call_node.args[1]

            # Evaluate arguments into temporary variables
            temp_num = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_num, arg_num_node, current_func_info.get('name') if current_func_info else None)

            temp_ptr = func_core.get_temp_var()
            func_expressions.translate_expression_recursive(temp_ptr, arg_ptr_node, current_func_info.get('name') if current_func_info else None)

            # Load sprite number into X register
            gen_code.append(f"    LDX {temp_num}      ; Carica numero sprite in X")

            # Load pointer value into A register
            gen_code.append(f"    LDA {temp_ptr}      ; Carica valore puntatore in A")

            # Call the routine
            gen_code.append("    JSR sprite_set_pointer")
            used_routines.add('sprite_set_pointer')

            gen_code.append(f"    ; --- Fine chiamata a sprite_set_pointer ---")
            func_core.release_temp_var(temp_num)
            func_core.release_temp_var(temp_ptr)
            return # Chiamata gestita

        # --- Gestione funzioni built-in (logica esistente) ---
        if func_name == 'print':
            func_core.process_print_call(call_node, error_handler_func, current_func_info, func_expressions)
            return
        # ... qui andrebbe la gestione di altre funzioni built-in come int(), float(), etc.

        # --- Gestione funzioni definite dall'utente (NUOVA LOGICA BASATA SU STACK) ---
        if func_name in globals.defined_functions:
            func_info = globals.defined_functions[func_name]

            # Controllo del numero di argomenti
            if len(call_node.args) != len(func_info['params']):
                report_error(f"Function '{func_name}' called with {len(call_node.args)} arguments, but expected {len(func_info['params'])}.", node=call_node)
                return

            gen_code.append(f"    ; --- Preparazione chiamata a {func_name} ---")

            # 1. Valuta e PUSH-a gli argomenti sullo stack (in ordine inverso)
            # La convenzione "cdecl" (argomenti da destra a sinistra) semplifica la gestione
            # da parte della funzione chiamata (il "callee").
            total_arg_size = 0
            for arg_node in reversed(call_node.args):
                # Valuta l'espressione dell'argomento. Il risultato finisce in A/X.
                _evaluate_expression_to_ax(arg_node, error_handler_func, current_func_info)

                # Push del risultato a 16 bit (A=high, X=low) sullo stack
                gen_code.append("    JSR push_word_ax")
                used_routines.add('push_word_ax')

                # Per ora, assumiamo che tutti gli argomenti siano parole di 2 byte.
                total_arg_size += 2

            # 2. Chiama la funzione
            gen_code.append(f"    JSR {func_info['label']}")

            # 3. Pulisci lo stack rimuovendo gli argomenti (responsabilità del caller)
            if total_arg_size > 0:
                gen_code.extend([
                    f"    ; Caller pulisce {total_arg_size} byte di argomenti dallo stack",
                    "    CLC",
                    f"    LDA ${globals.STACK_POINTER_ZP:02X}",
                    f"    ADC #{total_arg_size}",
                    f"    STA ${globals.STACK_POINTER_ZP:02X}",
                    f"    LDA ${globals.STACK_POINTER_ZP+1:02X}",
                    f"    ADC #0",
                    f"    STA ${globals.STACK_POINTER_ZP+1:02X}"
                ])

            # Il valore di ritorno si trova ora in A/X, pronto per essere usato.
            # Poiché siamo in process_expr_node (una chiamata standalone), il valore viene scartato.
            gen_code.append(f"    ; --- Fine chiamata a {func_name} (valore di ritorno in A/X scartato) ---")

        else:
            report_error(f"Chiamata a funzione non definita '{func_name}'.", node=call_node)
    else:
        # Per altre espressioni standalone (es. una riga con solo `5`), valutale e scarta il risultato.
        _evaluate_expression_to_ax(node.value, error_handler_func, current_func_info)

# --- Funzioni placeholder per gli altri processori di nodi AST ---
# Queste conterranno le implementazioni per le altre parti del compilatore.

def process_assign_node(node, current_func_info=None):
    """Processes an ast.Assign node."""
    # --- NEW: Handle function calls that return a value ---
    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Call):
        target_var_name = node.targets[0].id
        call_node = node.value
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id

            if func_name in ['sprite_check_collision_sprite', 'sprite_check_collision_data']:
                if len(call_node.args) != 0:
                    report_error(f"Function '{func_name}' expects 0 arguments, got {len(call_node.args)}.", node=call_node)
                    return

                # Get resolved variable name (handles local vs global scope)
                current_func_name = current_func_info.get('name') if current_func_info else None
                resolved_var_name = target_var_name
                if current_func_name:
                    mangled_name = _get_mangled_local_var_name(current_func_name, target_var_name)
                    if mangled_name in variables:
                        resolved_var_name = mangled_name

                gen_code.append(f"    ; --- Chiamata a {func_name} con assegnazione a {resolved_var_name} ---")
                gen_code.append(f"    JSR {func_name}")
                used_routines.add(func_name)
                # The result is in the A register (8-bit)
                gen_code.append(f"    STA {resolved_var_name}      ; Salva il risultato (LSB)")
                gen_code.append(f"    LDA #0")
                gen_code.append(f"    STA {resolved_var_name}+1    ; Pulisce MSB (valore a 8 bit)")
                gen_code.append(f"    ; --- Fine chiamata ---")
                return # Assignment handled

    # --- Original logic for other assignments ---
    if len(node.targets) > 1:
        report_error("Multiple assignment targets not supported.", node=node)
        return

    target = node.targets[0]
    if isinstance(target, ast.Name):
        var_name = target.id
        current_func_name = current_func_info.get('name') if current_func_info else None

        resolved_var_name = var_name
        if current_func_name:
            mangled_name = _get_mangled_local_var_name(current_func_name, var_name)
            if mangled_name in variables:
                resolved_var_name = mangled_name

        func_expressions.translate_expression_recursive(resolved_var_name, node.value, current_func_name)
    else:
        if isinstance(target, ast.Subscript):
            func_dict.handle_dict_assignment(node)
        else:
            report_error(f"Assignment to target of type {type(target).__name__} not supported.", node=target)

def process_function_def_node(node, error_handler_func):
    func_name = node.name
    func_info = globals.defined_functions[func_name]
    func_label = func_info['label']
    ret_label = func_info['ret_label']

    gen_code.append(f"\n{func_label}:")
    gen_code.append(f"    ; --- Function Prologue for {func_name} ---")

    # 1. Save old Frame Pointer (FP) onto the stack
    #    We need to load the FP address into TEMP_PTR1 for push_word_from_addr
    gen_code.extend([
        f"    LDA #<{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1:02X}",
        f"    LDA #>{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1+1:02X}",
        f"    JSR push_word_from_addr"
    ])
    used_routines.add('push_word_from_addr')

    # 2. Set new Frame Pointer (FP) to current Stack Pointer (SP)
    gen_code.extend(func_core._generate_copy_2_bytes( # Pass ZP addresses as integers
        globals.STACK_POINTER_ZP, globals.FRAME_POINTER_ZP
    ))

    # 3. Allocate space for local variables
    total_locals_size = func_info.get('total_locals_size', 0)
    if total_locals_size > 0:
        gen_code.append(f"    ; Allocate {total_locals_size} bytes for local variables")
        # Decrement SP by total_locals_size
        gen_code.extend([
            f"    SEC", # Set Carry for subtraction
            f"    LDA ${globals.STACK_POINTER_ZP:02X}",
            f"    SBC #{total_locals_size & 0xFF}",
            f"    STA ${globals.STACK_POINTER_ZP:02X}",
            f"    LDA ${globals.STACK_POINTER_ZP+1:02X}",
            f"    SBC #{(total_locals_size >> 8) & 0xFF}",
            f"    STA ${globals.STACK_POINTER_ZP+1:02X}"
        ])

    gen_code.append(f"    ; --- End Function Prologue ---")

    # Process function body
    current_func_info = {'name': func_name, 'params': func_info['params']}
    for statement in node.body:
        if isinstance(statement, ast.Expr):
            process_expr_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.Assign):
            process_assign_node(statement, current_func_info)
        elif isinstance(statement, ast.Return):
            # Handle return statement
            if statement.value:
                return_type = func_info.get('return_type', 'unknown')
                if return_type == 'float':
                    # Evaluate expression directly into FP1
                    temp_ret_val_var = func_core.get_temp_var()
                    func_expressions.translate_expression_recursive(temp_ret_val_var, statement.value, current_func_info)
                    gen_code.extend(func_core._generate_load_float_to_fp1(temp_ret_val_var))
                    func_core.release_temp_var(temp_ret_val_var)
                else: # Assume int (2 bytes)
                    # Evaluate expression into A/X
                    _evaluate_expression_to_ax(statement.value, error_handler_func, current_func_info)
                    # A/X already holds the return value.

            gen_code.append(f"    JMP {ret_label}") # Jump to epilogue
        elif isinstance(statement, ast.If):
            process_if_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.For):
            process_for_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.While):
            process_while_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.Global):
            pass # Handled in collection pass
        else:
            report_error(f"Unhandled statement type in function '{func_name}': {type(statement).__name__}", node=statement, level="WARNING")

    # Function Epilogue (if no explicit return or at the end of function)
    gen_code.append(f"\n{ret_label}:")
    gen_code.append(f"    ; --- Function Epilogue for {func_name} ---")

    # 1. Deallocate local variables (restore SP from FP)
    gen_code.extend(func_core._generate_copy_2_bytes( # Pass ZP addresses as integers
        globals.FRAME_POINTER_ZP, globals.STACK_POINTER_ZP
    ))

    # 2. Restore old Frame Pointer (FP) from stack
    gen_code.extend([
        f"    LDA #<{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1:02X}",
        f"    LDA #>{globals.FRAME_POINTER_ZP:04X}",
        f"    STA ${globals.TEMP_PTR1+1:02X}",
        f"    JSR pop_word_to_addr"
    ])
    used_routines.add('pop_word_to_addr')

    # 3. Return from subroutine
    gen_code.append(f"    RTS")
    gen_code.append(f"    ; --- End Function Epilogue ---")

def process_for_node(node, error_handler_func, current_func_info=None): # type: ignore
    """
    Processes an ast.For node.
    Supports 'for i in range(stop)', 'for i in range(start, stop)',
    and 'for i in range(start, stop, step)'.
    """
    # 1. Validate the loop structure
    if not isinstance(node.iter, ast.Call) or not isinstance(node.iter.func, ast.Name) or node.iter.func.id != 'range':
        report_error("For loops are only supported with range()", node=node.iter)
        return

    num_args = len(node.iter.args)
    if not (1 <= num_args <= 3):
        report_error(f"range() expects 1, 2, or 3 arguments, got {num_args}", node=node.iter)
        return

    if not isinstance(node.target, ast.Name):
        report_error("For loop target must be a simple variable name", node=node.target)
        return

    # 2. Setup and argument parsing
    loop_var_name = node.target.id
    current_func_name = current_func_info.get('name') if current_func_info else None
    resolved_loop_var_name = func_core.resolve_variable_name(loop_var_name, current_func_name) # type: ignore

    # Allocate temp vars for start, stop, step
    start_val_var = func_core.get_temp_var()
    stop_val_var = func_core.get_temp_var()
    step_val_var = func_core.get_temp_var()

    # Get expression nodes for start, stop, step based on number of arguments
    if num_args == 1:
        start_node = ast.Constant(value=0)
        stop_node = node.iter.args[0]
        step_node = ast.Constant(value=1)
    elif num_args == 2:
        start_node = node.iter.args[0]
        stop_node = node.iter.args[1]
        step_node = ast.Constant(value=1)
    else:  # num_args == 3
        start_node = node.iter.args[0]
        stop_node = node.iter.args[1]
        step_node = node.iter.args[2]

    # Create labels
    for_start_label = func_core.create_label("for_start", str(globals.label_counter))
    for_end_label = func_core.create_label("for_end", str(globals.label_counter))
    for_pos_step_loop_label = func_core.create_label("for_pos_step_loop", str(globals.label_counter))
    globals.label_counter += 1

    gen_code.append(f"\n    ; --- For loop for '{loop_var_name}' with extended range() ---")

    # 3. Evaluate start, stop, step values
    gen_code.append(f"    ; Evaluate range() arguments")
    func_expressions.translate_expression_recursive(start_val_var, start_node, current_func_name)
    func_expressions.translate_expression_recursive(stop_val_var, stop_node, current_func_name)
    func_expressions.translate_expression_recursive(step_val_var, step_node, current_func_name)

    # 4. Initialize loop variable
    gen_code.append(f"    ; Initialize loop variable '{resolved_loop_var_name}' from start value")
    gen_code.extend(func_core._generate_copy_2_bytes(start_val_var, resolved_loop_var_name))

    # 5. Loop Start and condition check
    gen_code.append(f"\n{for_start_label}:")
    # Check if step is negative
    gen_code.append(f"    LDA {step_val_var}+1 ; Check sign of step value")
    gen_code.append(f"    BPL {for_pos_step_loop_label} ; If positive or zero, jump to positive step logic")

    # --- Negative Step Logic (step < 0) ---
    # Condition: loop_var > stop_var. Exit if loop_var <= stop_var
    gen_code.append(f"    ; Negative step condition: check if {resolved_loop_var_name} <= {stop_val_var}")
    gen_code.extend([
        f"    LDA {resolved_loop_var_name}+1",
        f"    CMP {stop_val_var}+1",
        f"    BCC {for_end_label}",          # if loop_h < stop_h, then loop_var < stop_var, so exit.
        f"    BNE {for_start_label}_continue", # if loop_h > stop_h, then loop_var > stop_var, so continue.
        # High bytes are equal, check low bytes
        f"    LDA {resolved_loop_var_name}",
        f"    CMP {stop_val_var}",
        f"    BCC {for_end_label}",          # if loop_l < stop_l, then loop_var < stop_var, so exit.
        f"    BEQ {for_end_label}",          # if loop_l == stop_l, then loop_var == stop_var, so exit.
    ])
    gen_code.append(f"    JMP {for_start_label}_continue") # loop_var > stop_var, continue

    # --- Positive Step Logic (step >= 0) ---
    gen_code.append(f"\n{for_pos_step_loop_label}:")
    # Condition: loop_var < stop_var. Exit if loop_var >= stop_var
    gen_code.append(f"    ; Positive step condition: check if {resolved_loop_var_name} >= {stop_val_var}")
    gen_code.extend([
        f"    LDA {resolved_loop_var_name}+1",
        f"    CMP {stop_val_var}+1",
        f"    BCC {for_start_label}_continue", # if loop_h < stop_h, continue
        f"    BNE {for_end_label}",          # if loop_h > stop_h, exit
        f"    LDA {resolved_loop_var_name}",
        f"    CMP {stop_val_var}",
        f"    BCS {for_end_label}"           # if loop_l >= stop_l, exit
    ])

    gen_code.append(f"\n{for_start_label}_continue:")

    # 6. Process loop body
    for statement in node.body:
        # Dispatch statement processing
        if isinstance(statement, ast.Assign): process_assign_node(statement, current_func_info)
        elif isinstance(statement, ast.Expr): process_expr_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.If): process_if_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.While): process_while_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.For): process_for_node(statement, error_handler_func, current_func_info)
        else:
            report_error(f"Unhandled statement type in for-loop body: {type(statement).__name__}", node=statement, level="WARNING")

    # 7. Update loop variable by adding step
    gen_code.append(f"    ; Update loop variable: {resolved_loop_var_name} += step")
    gen_code.extend([
        "    CLC",
        f"    LDA {resolved_loop_var_name}",
        f"    ADC {step_val_var}",
        f"    STA {resolved_loop_var_name}",
        f"    LDA {resolved_loop_var_name}+1",
        f"    ADC {step_val_var}+1",
        f"    STA {resolved_loop_var_name}+1"
    ])

    # 8. Jump back to start
    gen_code.append(f"    JMP {for_start_label}")

    # 9. End of loop
    gen_code.append(f"\n{for_end_label}:")
    gen_code.append(f"    ; --- End For loop ---")

    # 10. Cleanup
    func_core.release_temp_var(start_val_var)
    func_core.release_temp_var(stop_val_var)
    func_core.release_temp_var(step_val_var)

def process_while_node(node, error_handler_func, current_func_info=None):
    """Processes an ast.While node."""
    while_start_label = func_core.create_label("while_start", str(globals.label_counter))
    while_end_label = func_core.create_label("while_end", str(globals.label_counter))
    globals.label_counter += 1

    gen_code.append(f"\n{while_start_label}:")
    _evaluate_expression_to_ax(node.test, error_handler_func, current_func_info)
    gen_code.append("    ORA X") # Check if A/X is zero
    gen_code.append(f"    BEQ {while_end_label}")

    for statement in node.body:
        if isinstance(statement, ast.Assign): process_assign_node(statement, current_func_info)
        elif isinstance(statement, ast.Expr): process_expr_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.If): process_if_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.While): process_while_node(statement, error_handler_func, current_func_info)
        elif isinstance(statement, ast.For): process_for_node(statement, error_handler_func, current_func_info)
        else:
            report_error(f"Unhandled statement type in while-loop body: {type(statement).__name__}", node=statement, level="WARNING")

    gen_code.append(f"    JMP {while_start_label}")
    gen_code.append(f"{while_end_label}:")

def process_delete_node(node):
    gen_code.append(f"; Placeholder per Delete")

def process_if_node(node, error_handler_func, current_func_info=None):
    """Processes an ast.If node, including those inside functions."""
    else_label = func_core.create_label("if_else", str(globals.label_counter))
    end_if_label = func_core.create_label("if_end", str(globals.label_counter))
    globals.label_counter += 1

    # Evaluate the condition
    _evaluate_expression_to_ax(node.test, error_handler_func, current_func_info)

    # Check if the result in A/X is zero (False)
    gen_code.append("    ORA X")

    if node.orelse:
        gen_code.append(f"    BEQ {else_label}")
    else:
        gen_code.append(f"    BEQ {end_if_label}")

    # Process the 'if' body
    for statement in node.body:
        # Dispatch statement processing
        if isinstance(statement, (ast.Assign, ast.Expr, ast.If, ast.Return, ast.Global)):
            # A bit of a hack to avoid a full dispatcher function for now
            if isinstance(statement, ast.Assign): process_assign_node(statement, current_func_info)
            if isinstance(statement, ast.Expr): process_expr_node(statement, error_handler_func, current_func_info)
            if isinstance(statement, ast.If): process_if_node(statement, error_handler_func, current_func_info)
            if isinstance(statement, ast.For): process_for_node(statement, error_handler_func, current_func_info)
            if isinstance(statement, ast.While): process_while_node(statement, error_handler_func, current_func_info)
            if isinstance(statement, ast.Return):
                # Simplified return logic for inside an if
                if not current_func_info: continue
                func_info = globals.defined_functions[current_func_info['name']]
                _evaluate_expression_to_ax(statement.value, error_handler_func, current_func_info)
                gen_code.append(f"    JMP {func_info['ret_label']}")
        else:
            report_error(f"Unhandled statement type in if-body: {type(statement).__name__}", node=statement, level="WARNING")

    if node.orelse:
        gen_code.append(f"    JMP {end_if_label}")
        gen_code.append(f"{else_label}:")
        for statement in node.orelse:
            # Dispatch statement processing for else block
            if isinstance(statement, (ast.Assign, ast.Expr, ast.If, ast.Return, ast.Global)):
                if isinstance(statement, ast.Assign): process_assign_node(statement, current_func_info)
                if isinstance(statement, ast.Expr): process_expr_node(statement, error_handler_func, current_func_info)
                if isinstance(statement, ast.If): process_if_node(statement, error_handler_func, current_func_info)
                if isinstance(statement, ast.For): process_for_node(statement, error_handler_func, current_func_info)
                if isinstance(statement, ast.While): process_while_node(statement, error_handler_func, current_func_info)
            else:
                report_error(f"Unhandled statement type in else-body: {type(statement).__name__}", node=statement, level="WARNING")

    gen_code.append(f"{end_if_label}:")

def process_try_node(node, error_handler_func):
    gen_code.append(f"; Placeholder per Try block")
