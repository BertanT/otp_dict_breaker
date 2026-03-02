"""
__init__.py
Created on 2/17/26

Copyright (C) 2026 Mehmet Bertan Tarakcioglu

This file is part of OTP Dictionary Breaker.

OTP Dictionary Breaker is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OTP Dictionary Breaker is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with OTP Dictionary Breaker.
If not, see <https://www.gnu.org/licenses/>.
"""

from otp_dict_breaker.breaker import OTPDictBreaker
from otp_dict_breaker.tui import OTPDictBreakerTUI

__all__ = ["OTPDictBreaker", "OTPDictBreakerTUI"]