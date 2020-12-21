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
        test_db_path = os.path.join(sys.path[0], 'test_db.sqlite')
        self.chain: Blockchain = Blockchain(test_db_path)

        self.test_user_id: str = 'testuserid'
        self.test_user_id2: str = 'testuserid2'
        self.test_pass: str = 'password1'
        self.test_pass2: str = 'password2'
        self.test_choice = 'The Rhino Party'
        self.test_choice2 = 'The Even More Rhino Party'

        self.con = sqlite3.connect(test_db_path)
        self.cur = self.con.cursor()

        self.cur.execute('''CREATE TABLE IF NOT EXISTS uids(
                            id string PRIMARY KEY
                        )''')
        self.cur.executemany('''INSERT OR IGNORE INTO uids VALUES(?)''', [(self.test_user_id,), (self.test_user_id2,)])
        self.con.commit()

    def test_blockfinder_error(self):
        self.assertRaises(UserNotRegisteredError, self.chain.get_registration_block, 'invalidID')

    def test_nonexistant_registration(self):
        self.assertRaises(UserNotExistError, self.chain.register_user, 'invaliduserid', 'password')

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
