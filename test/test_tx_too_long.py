#!/usr/bin/env python
#*******************************************************************************
#*   Ledger Blue
#*   (c) 2016 Ledger
#*
#*  Licensed under the Apache License, Version 2.0 (the "License");
#*  you may not use this file except in compliance with the License.
#*  You may obtain a copy of the License at
#*
#*      http://www.apache.org/licenses/LICENSE-2.0
#*
#*  Unless required by applicable law or agreed to in writing, software
#*  distributed under the License is distributed on an "AS IS" BASIS,
#*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#*  See the License for the specific language governing permissions and
#*  limitations under the License.
#********************************************************************************
import pytest
from pathlib import Path
from utils import sign_tx, get_packed_path
from ragger.error import ExceptionRAPDU
from inspect import currentframe

# sending to AHXSMB19pWytwJ7vzvCw5aWmd1DUniDKRT
# too big TX, should generate error 0x6D08
rawText_00 = bytearray.fromhex(
    "0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e"
    +
    "0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e"
    +
    "0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e"
    +
    "0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e"
    +
    "0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e"
    +
    "0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e"
)
textToSign_00 = rawText_00 + get_packed_path()


def test_sign_tx_too_long(backend, firmware, navigator):
    path = Path(currentframe().f_code.co_name)
    # Sign Tx
    with pytest.raises(ExceptionRAPDU) as e:
        sign_tx(backend, firmware, navigator, textToSign_00, path, False)
    assert e.value.status == 0x6D08
