#!/usr/bin/env python
# *******************************************************************************
# *   NEO tests
# *   (c) 2023 Ledger
# *
# *  Licensed under the Apache License, Version 2.0 (the "License");
# *  you may not use this file except in compliance with the License.
# *  You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# *  Unless required by applicable law or agreed to in writing, software
# *  distributed under the License is distributed on an "AS IS" BASIS,
# *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# *  See the License for the specific language governing permissions and
# *  limitations under the License.
# ********************************************************************************
from utils import get_signed_public_key_and_validate, DEFAULT_PATH, ROOT_SCREENSHOT_PATH
from pathlib import Path
from inspect import currentframe
from ragger.navigator import NavInsID, NavIns
from time import sleep
import pytest


def test_display_address(backend, firmware, navigator):
    path = Path(currentframe().f_code.co_name)

    if firmware.device == "nanos":
        pytest.skip("Nano S app does not implement address display ui.")
    elif firmware.device == "stax":
        navigator.navigate_and_compare(
            # Use custom touch coordinates to account for warning approve
            # button position.
            ROOT_SCREENSHOT_PATH,
            path,
            [NavIns(NavInsID.TOUCH, (200, 520)), NavInsID.EXIT_FOOTER_TAP],
            screen_change_before_first_instruction=False)
    else:
        navigator.navigate_and_compare(
            # Use custom touch coordinates to account for warning approve
            # button position.
            ROOT_SCREENSHOT_PATH,
            path,
            [
                NavInsID.RIGHT_CLICK,
                NavInsID.BOTH_CLICK,
                NavInsID.RIGHT_CLICK,
                NavInsID.BOTH_CLICK,
            ],
            screen_change_before_first_instruction=False)

    # Get public key (this will update the UI to display the address)
    get_signed_public_key_and_validate(backend, DEFAULT_PATH)[1:]

    if firmware.device == "stax":
        navigator.navigate_and_compare(
            # Use custom touch coordinates to account for warning approve
            # button position.
            ROOT_SCREENSHOT_PATH,
            path,
            [NavIns(NavInsID.TOUCH, (200, 520)), NavInsID.EXIT_FOOTER_TAP],
            screen_change_before_first_instruction=False,
            snap_start_idx=3)
    else:
        navigator.navigate_and_compare(
            # Use custom touch coordinates to account for warning approve
            # button position.
            ROOT_SCREENSHOT_PATH,
            path,
            [
                NavInsID.RIGHT_CLICK,
                NavInsID.BOTH_CLICK,
                NavInsID.RIGHT_CLICK,
                NavInsID.BOTH_CLICK,
            ],
            screen_change_before_first_instruction=False,
            snap_start_idx=5)
