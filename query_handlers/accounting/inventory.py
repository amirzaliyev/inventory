"""
to be continued...
"""

from typing import Tuple


from resources.string import CALCULATING
from utils import Switch

inv_switch = Switch(name="inventory")


@inv_switch.register("results")
async def results() -> Tuple[str, None]:
    return CALCULATING, None
