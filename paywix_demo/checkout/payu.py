import hashlib
from checkout.utils import payu_config, post
from checkout.exceptions import AccessModeException, AuthHeaderMissingException
from checkout.decorators import validate_params, validator


class Payu():

    def __init__(self, merchant_key, merchant_salt, s_url, f_url, mode='TEST', auth_header=None):
        if mode.lower() not in ['test', 'live']:
            raise AccessModeException(mode)
        self.merchant_key = merchant_key
        self.merchant_salt = merchant_salt
        self.success_url = s_url
        self.failure_url = f_url
        self.base_url = payu_config.get(mode.lower(), 'test')
        self.auth_header = auth_header

    def generate_txnid(self, prefix=None, limit=20):
        hash_object = hashlib.sha256(b'randint(0,20)')
        txnid = f'{prefix} {hash_object.hexdigest()[0:limit]}'
        return txnid

    def generate_hash(self, hash_string):
        hash_value = hashlib.sha512(
            hash_string.encode('utf-8')).hexdigest().lower()
        return hash_value

    @validate_params('payu_request', 'payu', 'transaction')
    def transaction(self, **kwargs):
        kwargs.update({'key': self.merchant_key})
        hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1\
            |udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
        hash_string = ''
        hashVarsSeq = hashSequence.split('|')
        for hash_str in hashVarsSeq:
            try:
                hash_string += str(kwargs[hash_str])
            except Exception:
                hash_string += ''
            hash_string += '|'
        hash_string += self.merchant_salt
        data = kwargs
        data.update({
            'hashh': self.generate_hash(hash_string),
            'merchant_key': self.merchant_key,
            'surl': self.success_url,
            'furl': self.failure_url,
            'hash_string': hash_string,
            'service_provider': 'payu_paisa',
            'action': self.base_url
        })
        return data

    def verify_transaction(self, response_data):
        results = {}
        status = response_data.get('status')
        first_name = response_data.get('firstname')
        amount = response_data.get('amount')
        txnid = response_data.get('txnid')
        response_key = response_data.get('key')
        product_info = response_data.get('productinfo')
        email = response_data.get('email')
        response_hash = response_data.get("hash")
        add_charge = response_data.get('additionalCharges')
        hash_string = ""
        if add_charge:
            hash_string += f'{add_charge}|'

        hash_string += f'{self.merchant_salt}|{status}|||||||||||{email}|{first_name}|{product_info}|{amount}|{txnid}|{self.merchant_key}'
        generated_hash = self.generate_hash(hash_string)
        results.update({"return_data": response_data})
        results.update({
            'hash_string': hash_string,
            'generated_hash': generated_hash,
            'recived_hash': response_hash,
            'hash_verified': generated_hash == response_hash
        })
        return results

    def generate_header(self):
        header = {}
        header.update({
            "authorization": self.auth_header,
            "content-type": "application/json",
            "cache-control": "no-cache"
        })
        return header

    def api(self, method, data):
        if not self.auth_header:
            raise AuthHeaderMissingException(
                "Authentication Header is missing")

        if method == 'get_payment_status':

            # @validate_params('payu_payment_resp', 'payu', 'get_payment_response')
            # def get_payment_response(self, data):
            #     if not self.auth_header:
            #         raise AuthHeaderMissingException("Please initialize auth_header in Payu()")
            #     base_url = payu_config.get("api_test" if self.mode =="test" else "api_live")
            #     transactions = ("|").join(data.get('transaction_ids'))
            #     from_date = data.get("from", None)
            #     to_date = data.get("to", None)
            #     url = f'{base_url}/op/getPaymentResponse?merchantKey={merchant_key}\
            #         &merchantTransactionIds={transactions}&from={from_date}&to={to_date}'
            #     header = self.generate_header()
            #     connection = Connection(url, header)
            #     return connection.post()
