# test_graphics.py

test_cases = [
    {
        'name': 'Test GFX Turn On and Clear Screen',
        'code': """
gfx_turn_on()
gfx_clear_screen()
while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/test_gfx_on_clear.asm'
    },
    {
        'name': 'Test GFX Draw Line (Star)',
        'code': """
gfx_turn_on()
gfx_clear_screen()

# Draw the lines that form the star
draw_line(160, 100, 240, 40)
draw_line(240, 40, 260, 120)
draw_line(260, 120, 160, 160)
draw_line(160, 160, 60, 120)
draw_line(60, 120, 80, 40)
draw_line(80, 40, 160, 100)

# Loop forever to keep the image on screen
while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/test_gfx_draw_star.asm'
    },
    {
        'name': 'Test GFX Turn Off',
        'code': """
gfx_turn_on()
gfx_turn_off()
""",
        'expected': 'graphics/test_gfx_off.asm',
    },
    {
        'name': 'Test GFX Draw Ellipse and Circle',
        'code': """
gfx_turn_on()
gfx_clear_screen()

# Draw an ellipse
draw_ellipse(160, 100, 80, 40)

# Draw a circle (ellipse with equal radii)
draw_ellipse(60, 150, 30, 30)
""",
        'expected': 'graphics/test_gfx_draw_ellipse.asm'
    },
    {
        'name': 'graphics_draw_circle_simple',
        'code': """
gfx_turn_on()
gfx_clear_screen()
# Disegna un cerchio con valori costanti
draw_circle(120, 90, 40)
while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_draw_circle_simple.asm'
    },
    {
        'name': 'graphics_draw_circle_vars',
        'code': """
gfx_turn_on()
gfx_clear_screen()
# Disegna un cerchio usando variabili
x_center = 200
y_center = 110
radius = 60
draw_circle(x_center, y_center, radius)
while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_draw_circle_vars.asm'
    },
    {
        'name': 'graphics_draw_ellipse_expressions',
        'code': """
gfx_turn_on()
gfx_clear_screen()
# Disegna un'ellisse usando espressioni come argomenti
offset_x = 10
offset_y = 5
draw_ellipse(160 + offset_x, 100 - offset_y, 40 * 2, 60 // 2)
while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_draw_ellipse_expressions.asm'
    },
    {
        'name': 'graphics_draw_rect_simple',
        'code': """
gfx_turn_on()
gfx_clear_screen()
# Disegna un rettangolo con valori costanti
draw_rect(50, 50, 270, 150)
while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_draw_rect_simple.asm'
    },
    {
        'name': 'graphics_sprite_set_pos',
        'code': """
# Imposta la posizione dello sprite 0 a (150, 100) usando variabili
sprite_num = 0
x_pos = 150
y_pos = 100
sprite_set_pos(sprite_num, x_pos, y_pos)

# Imposta la posizione dello sprite 1 a (180, 120) con costanti
sprite_set_pos(1, 180, 120)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_set_pos.asm'
    },
    {
        'name': 'graphics_sprite_color_and_enable',
        'code': """
# Abilita sprite 0 e 2 (maschera 1+4=5)
sprite_enable(5)

# Imposta il colore dello sprite 0 a blu (6)
sprite_num = 0
color_code = 6
sprite_set_color(sprite_num, color_code)

# Imposta il colore dello sprite 2 a giallo (7) con costanti
sprite_set_color(2, 7)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_color_and_enable.asm'
    },
    {
        'name': 'graphics_sprite_disable_and_msb',
        'code': """
# Abilita sprite 0 e 1 (maschera 1+2=3)
sprite_enable(3)

# Imposta la posizione dello sprite 1 a X>255
# LSB di X = 300-256 = 44
sprite_set_pos(1, 44, 100)
# Imposta il bit MSB per lo sprite 1 (maschera 2)
sprite_set_x_msb(2)

# Disabilita lo sprite 0 (maschera 1)
sprite_disable(1)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_disable_and_msb.asm'
    },
    {
        'name': 'graphics_sprite_expand',
        'code': """
# Espande lo sprite 0 in Y e lo sprite 1 in X
y_expand_mask = 1 # sprite 0
x_expand_mask = 2 # sprite 1
sprite_expand_xy(y_expand_mask, x_expand_mask)

# Espande lo sprite 2 sia in X che in Y usando costanti
sprite_expand_xy(4, 4)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_expand.asm'
    },
    {
        'name': 'graphics_sprite_msb_clear',
        'code': """
# Imposta la posizione dello sprite 1 a X>255
# LSB di X = 300-256 = 44
sprite_set_pos(1, 44, 100)
# Imposta il bit MSB per lo sprite 1 (maschera 2)
sprite_set_x_msb(2)

# Ora cancella il bit MSB per lo sprite 1, riportando la sua X a 44
msb_mask_to_clear = 2
sprite_set_x_msb_clear(msb_mask_to_clear)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_msb_clear.asm'
    },
    {
        'name': 'graphics_sprite_set_pointer',
        'code': """
# Set pointer for sprite 0 to point to data block at $3000 (pointer value $C0 = 192)
sprite_set_pointer(0, 192)

# Set pointer for sprite 1 using variables
s_num = 1
ptr_val = 193 # for data at $3040
sprite_set_pointer(s_num, ptr_val)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_set_pointer.asm'
    },
    {
        'name': 'graphics_sprite_priority',
        'code': """
# Set sprite 0 to be behind background graphics (mask=1)
sprite_set_priority(1)

# Set sprite 3 to be behind background using a variable
prio_mask = 8 # bit 3
sprite_set_priority(prio_mask)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_priority.asm'
    },
    {
        'name': 'graphics_sprite_multicolor',
        'code': """
# Set sprite 1 to multicolor mode using a constant
sprite_set_multicolor(2) # mask for sprite 1 is bit 1 = 2

# Set sprite 2 to multicolor mode using a variable
mc_mask = 4 # mask for sprite 2 is bit 2 = 4
sprite_set_multicolor(mc_mask)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_multicolor.asm'
    },
    {
        'name': 'graphics_sprite_multicolor_colors',
        'code': """
# Set multicolor colors using variables
mc1 = 1 # black
mc2 = 7 # yellow
sprite_set_multicolor_colors(mc1, mc2)

# Set multicolor colors using constants
sprite_set_multicolor_colors(2, 11) # red, light cyan

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_multicolor_colors.asm'
    },
    {
        'name': 'graphics_sprite_collision_check',
        'code': """
# Enable some sprites to check for collisions
sprite_enable(3) # sprite 0 and 1
sprite_set_pos(0, 100, 100)
sprite_set_pos(1, 102, 101) # Position them to collide

# Check for sprite-sprite collision and store the result
sprite_collisions = sprite_check_collision_sprite()

# Check for sprite-data collision and store the result
data_collisions = sprite_check_collision_data()

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_collision_check.asm'
    },
    {
        'name': 'graphics_sprite_create_from_data',
        'code': """
# Create sprite 0 from data located at address $4000
sprite_create_from_data(0, 0x4000)

# Create sprite 1 using variables
sprite_to_create = 1
data_address = 0x4040
sprite_create_from_data(sprite_to_create, data_address)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_create_from_data.asm'
    },
    {
        'name': 'graphics_sprite_set_pointer',
        'code': """
# Set pointer for sprite 0 to point to data block at $3000 (pointer value $C0 = 192)
sprite_set_pointer(0, 192)

# Set pointer for sprite 1 using variables
s_num = 1
ptr_val = 193 # for data at $3040
sprite_set_pointer(s_num, ptr_val)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_set_pointer.asm'
    },
    {
        'name': 'graphics_sprite_priority',
        'code': """
# Set sprite 0 to be behind background graphics (mask=1)
sprite_set_priority(1)

# Set sprite 3 to be behind background using a variable
prio_mask = 8 # bit 3
sprite_set_priority(prio_mask)

while True: # pragma: no cover
    pass # pragma: no cover
""",
        'expected': 'graphics/graphics_sprite_priority.asm'
    }
]
