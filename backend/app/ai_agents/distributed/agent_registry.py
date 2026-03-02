"""
Single source of truth for agent names.
Every file that references an agent by name imports from here.
"""

HAWK = 'sir_hawkington'
TERRY = 'meth_snail'
HAMSTERS = 'hamsters'
QSP = 'quantum_shadow_people'
VIC20 = 'vic_20_sage'
STICK = 'the_stick'

ALL_AGENTS = frozenset([HAWK, TERRY, HAMSTERS, QSP, VIC20, STICK])
SPECIALISTS = frozenset([TERRY, HAMSTERS, QSP])
COORDINATION = frozenset([HAWK, VIC20, STICK])

RESOURCE_TO_SPECIALIST = {
    'cpu': TERRY,
    'memory': TERRY,
    'swap': TERRY,
    'disk': HAMSTERS,
    'network': QSP,
}
