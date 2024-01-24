""" Hash based (Counter) OTP Implementation """

import random
import pyotp


class CryptoOTP:
    """ A base class for the Hash-based OTP  """

    def __init__(self):
        self.counter    = random.randint(1000, 1000000)
        self.basesecret = pyotp.random_hex()
        self.hotp       = pyotp.HOTP(self.basesecret)

    def _increment_counter(self):
        """ increment the otp counter """

        self.counter = self.counter + 1

    def _verify_otp_entry(self, proposed_otp):
        """ private method to verify OTP """

        return self.hotp.verify(proposed_otp, self.counter)

    def verify_otp_entry(self, otp):
        """ public method to verify OTP """

        # To be safe, default is False
        verified = False
        if self._verify_otp_entry(otp):
            self.counter = self.counter + 1
            verified = True

        return verified

    def generate_provision_url(self, user_email):
        """" Generate HOTP provisioning URL """

        return pyotp.hotp.HOTP(self.basesecret).provisioning_uri(
            name=user_email, issuer_name="CryptoAdvisor"
        )
