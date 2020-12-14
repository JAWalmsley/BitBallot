# Jack Walmsley 2020-12-04
import unittest

from cryptography.exceptions import InvalidSignature

from blockchain import *
from exceptions import *


class BlockchainTests(unittest.TestCase):
    def setUp(self):
        """
        Sets up the testing suite, creating a dummy blockchain
        """
        self.chain: Blockchain = Blockchain()
        self.test_pass: str = 'password1'
        self.test_pass2: str = 'password2'
        self.test_user_id: str = 'testuserid'
        self.test_user_id2: str = 'testuserid2'
        self.test_choice = 'The Rhino Party'
        self.test_choice2 = 'The Even More Rhino Party'

    def test_blockfinder_error(self):
        self.assertRaises(UserNotRegisteredError, self.chain.get_registration_block, 'invalidID')

    def register_user(self):
        """
        Tests the registration function of the blockchain
        """
        first_block = self.chain.register_user(self.test_user_id, self.test_pass)
        self.assertIsInstance(first_block, RegisterBlock)
        self.assertEqual(self.chain.get_registration_block(self.test_user_id), first_block)

        self.assertRaises(UserAlreadyExistsError, self.chain.register_user, self.test_user_id, self.test_pass)

        second_block = self.chain.register_user(self.test_user_id2, self.test_pass2)
        self.assertEqual(second_block.prev_hash, first_block.get_hash())

    def cast_vote(self):
        """
        Tests using the registered user to vote
        """
        with self.assertRaises(InvalidSignature):
            self.chain.cast_vote(self.test_user_id, 'badpassword', 'The Hippopotamus Party')

        first_block = self.chain.cast_vote(self.test_user_id, self.test_pass, self.test_choice)
        self.assertIsInstance(first_block, VoteBlock)

        second_block = self.chain.cast_vote(self.test_user_id2, self.test_pass2, self.test_choice)
        self.assertEqual(second_block.prev_hash, first_block.get_hash())

    def test_monolithic(self):
        self.register_user()
        self.cast_vote()

if __name__ == '__main__':
    unittest.main()
