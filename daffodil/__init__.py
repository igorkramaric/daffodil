import pyximport
pyximport.install()

from daffodil.daffodil_parser import DaffodilPy as Daffodil
from daffodil.predicate import DictionaryPredicateDelegate
from daffodil.hstore_predicate import HStoreQueryDelegate
from daffodil.pretty_print import PrettyPrintDelegate
from daffodil.key_expectation_delegate import KeyExpectationDelegate
from daffodil.simulation_delegate import SimulationMatchingDelegate

default_app_config = 'daffodil.apps.DaffodilAppConfig'