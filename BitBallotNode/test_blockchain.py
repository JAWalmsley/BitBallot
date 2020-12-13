# Jack Walmsley 2020-12-04
import unittest
import base64

from cryptography.exceptions import InvalidSignature

from blockchain import *
from exceptions import *


class BlockchainTests(unittest.TestCase):
    def setUp(self):
        """
        Sets up the testing suite, creating a dummy blockchain
        """
        self.chain: Blockchain = Blockchain()
        self.testkey = ("MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJnfSpdYCdQGPakzj4UVJDM5vkrnc0aJ\n"
                        "1LaSu64PuRvaOWBo8AkG/E4M74bn/inAKsnel695SXG9k2fg73rFlPkCAwEAAQ==")
        self.testkey: rsa.RSAPrivateKey = rsa.generate_private_key(65537, 4096)
        self.testkey2: rsa.RSAPrivateKey = rsa.generate_private_key(65537, 4096)
        self.test_user_id: str = 'testuserid'
        self.test_user_id2: str = 'secondtestuserid'

    def register_user(self):
        """
        Tests the registration function of the blockchain
        """

        # We do ultimately want bytes for keys, but this data will arrive from client over HTTP, and will be a string
        public_key_str = self.testkey.public_key().public_bytes(serialization.Encoding.PEM,
                                                                serialization.PublicFormat.SubjectPublicKeyInfo).decode(
            'utf-8')
        public_key_str2 = self.testkey2.public_key().public_bytes(serialization.Encoding.PEM,
                                                                  serialization.PublicFormat.SubjectPublicKeyInfo).decode(
            'utf-8')

        self.assertRaises(UserNotRegisteredError, self.chain.get_registration_block, 'invalidID')

        first_block = self.chain.register_user(self.test_user_id, public_key_str)
        self.assertIsInstance(first_block, RegisterBlock)
        self.assertEqual(self.chain.get_registration_block(self.test_user_id), first_block)

        second_block = self.chain.register_user(self.test_user_id2, public_key_str2)
        self.assertEqual(second_block.prev_hash, first_block.get_hash())

    def cast_vote(self):
        """
        Tests using the registered user to vote
        """
        choice1 = 'The Rhino Party'
        choice2 = 'The Even More Rhino Party'
        pad = padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        )

        with self.assertRaises(InvalidSignature):
            self.chain.cast_vote(self.test_user_id, base64.urlsafe_b64encode(b'invalidsignature'), 'The Hippopotamus Party')

        # RSAPrivateKey.sign() returns a bytearray which is ultimately what we want, but this will be arriving from a
        # client over HTTP so will be strings. Therefore we convert bytes to base64 encoded str
        sig = base64.urlsafe_b64encode(self.testkey.sign(choice1.encode(), pad, hashes.SHA256())).decode()
        first_block = self.chain.cast_vote(self.test_user_id, sig, choice1)
        self.assertIsInstance(first_block, VoteBlock)

        sig = base64.urlsafe_b64encode(self.testkey2.sign(choice2.encode(), pad, hashes.SHA256())).decode()
        second_block = self.chain.cast_vote(self.test_user_id2, sig, choice2)
        self.assertEqual(second_block.prev_hash, first_block.get_hash())

    def test_blockchain(self):
        self.register_user()
        self.cast_vote()


if __name__ == '__main__':
    unittest.main()
