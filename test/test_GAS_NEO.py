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
from utils import get_packed_path, sign_and_validate

# sending to AHXSMB19pWytwJ7vzvCw5aWmd1DUniDKRT
# sending 0.001 GAS
#             80028000b38000000185e7e907cc5c5683e7fc926ba4be613d1810aebe14686b3675ee27d2476e5201000002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60a08601000000000013354f4f5d3f989a221c794271e0bb2471c2735ee72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e23f01000000000013354f4f5d3f989a221c794271e0bb2471c2735e8000002c80000378800000000000000000000000
rawText_00 = bytearray.fromhex("8000000185e7e907cc5c5683e7fc926ba4be613d1810aebe14686b3675ee27d2476e5201000002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60a08601000000000013354f4f5d3f989a221c794271e0bb2471c2735ee72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e23f01000000000013354f4f5d3f989a221c794271e0bb2471c2735e")
textToSign_00 = rawText_00 + get_packed_path()

# sending 1 NEO
#             8002800077800000018d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000019b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc500e1f5050000000013354f4f5d3f989a221c794271e0bb2471c2735e8000002c80000378800000000000000000000000
rawText_01 = bytearray.fromhex("800000018d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000019b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc500e1f5050000000013354f4f5d3f989a221c794271e0bb2471c2735e")
textToSign_01 = rawText_01 + get_packed_path()

# claiming GAS
#             80028000de0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e8000002c80000378800000000000000000000000
rawText_02 = bytearray.fromhex("0200048d121f4bc2bf104e547e85d680780fe629c2b3ce89ac73e0ff02feb572bb98e00000e47d4e3d0563a53232466fa7752b28db6c0485ee79e57dacb2646418f4e7ffd400002101dd269ec13b66360b29eb6ac78ba44b772b2b6369b7dd5ff8dcd5dd1aafa00000a5c04ecb7ff482474062fe0cbe030e653c77d28545a38490780f33be7469cdae0000000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60276501000000000013354f4f5d3f989a221c794271e0bb2471c2735e")
textToSign_02 = rawText_02 + get_packed_path()

def test_send_gas(backend, firmware, navigator):
    sign_and_validate(backend, firmware, navigator, textToSign_00)

def test_send_neo(backend, firmware, navigator):
    sign_and_validate(backend, firmware, navigator, textToSign_01)

def test_claim_gas(backend, firmware, navigator):
    sign_and_validate(backend, firmware, navigator, textToSign_02)

# signedPublicKey = dongle.exchange(
#     bytes(bytearray.fromhex("80080000FF" + bipp44_path)))
# print("signedPublicKey [" + str(len(signedPublicKey)) +
#       "] " + signedPublicKey.hex().upper())
# signature = signedPublicKey[67:]
# print("signature [" + str(len(signature)) + "] " + signature.hex().upper())
