import pprint

from cassiopeia import Region
from lib.extractors.porofessor_extractor import get_match_data

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(get_match_data('Hide on bush', Region.korea.value))
