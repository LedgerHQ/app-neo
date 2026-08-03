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
from pathlib import Path
from typing import Any, cast

from ragger.backend.interface import BackendInterface
from ragger.firmware.touch.positions import POSITIONS
from ragger.navigator import Navigator, NavIns, NavInsID
from utils import DEFAULT_PATH, get_signed_public_key_and_validate


def test_display_address(
    backend: BackendInterface,
    navigator: Navigator,
    default_screenshot_path: Path,
    test_name: str,
) -> None:
    device = backend.device

    instructions: list[NavIns | NavInsID] = []
    if device.touchable:
        # Use custom touch coordinates to account for warning approve
        # button position.
        coord = cast(Any, POSITIONS["UseCaseHomeExt"])[device.type]["action"]
        instructions += [NavIns(NavInsID.TOUCH, coord), NavInsID.CENTERED_FOOTER_TAP]
        start_index = 3
    else:
        instructions += [
            NavInsID.RIGHT_CLICK,
            NavInsID.BOTH_CLICK,
            NavInsID.RIGHT_CLICK,
            NavInsID.BOTH_CLICK,
        ]
        start_index = 5

    navigator.navigate_and_compare(
        default_screenshot_path,
        test_name,
        instructions,
        screen_change_before_first_instruction=False,
    )

    # Get public key (this will update the UI to display the address)
    _ = get_signed_public_key_and_validate(backend, DEFAULT_PATH)[1:]

    navigator.navigate_and_compare(
        default_screenshot_path,
        test_name,
        instructions,
        screen_change_before_first_instruction=False,
        snap_start_idx=start_index,
    )
