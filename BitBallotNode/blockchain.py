# Jack Walmsley 2020-12-02
import abc
import base64
import struct
from datetime import datetime

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec

from exceptions import *


class Block:
    def __init__(self, prev_hash: bytes, time: float, user_id: str):
        """
        Base class for all blockchain blocks

        :param prev_hash: The hash of the previous block in the chain
        :param time: The time this block was created
        :param user_id:
        """
        self.prev_hash = prev_hash
        self.time = time
        self.user_id = user_id

    @abc.abstractmethod
    def __dict__(self):
        """
        A dictionary representation of the block

        :return: dict of this block
        :rtype dict
        """
        return

    @abc.abstractmethod
    def get_hash(self):
        """
        The SHA-256 hash of the contents of the block

        :return: hash of this block
        :rtype str
        """
        return

    @staticmethod
    def password_to_key(password: str):
        """
        Derives a private key from the given password

        :param password: The password to derive key from
        :return: A private key derived from the password
        :rtype: ec.EllipticCurvePrivateKey
        """
        curve = ec.SECP256R1()  # Elliptic curve
        digest = hashes.Hash(hashes.SHA256())
        digest.update(password.encode())
        password_int = int.from_bytes(digest.finalize(), "big")
        return ec.derive_private_key(password_int, curve)


class RegisterBlock(Block):
    def __init__(self, prev_hash: bytes, time: float, user_id: str, password: str):
        """
        A block announcing a voter's registration

        :param prev_hash: The hash of the previous block
        :param time: The timestamp the block was created
        :param user_id: The user_id of the new voter
        :param password: The password of the new voter, for deriving cryptographic keys
        """
        super().__init__(prev_hash, time, user_id)

        # Derive a public key from the password. Add user_id to password as salt
        self.public_key: ec.EllipticCurvePublicKey = Block.password_to_key(password+user_id).public_key()

    def __dict__(self):
        """
        A dictionary representation of the block

        :return: dict of this block
        :rtype dict
        """
        result = {}
        result['block_type'] = 'register'
        result['prev_hash'] = base64.b64encode(self.prev_hash).decode()
        result['timestamp'] = self.time
        result['user_id'] = self.user_id
        result['public_key'] = base64.b64encode(self.public_key.public_bytes(serialization.Encoding.X962,
                                                                             serialization.PublicFormat.CompressedPoint)).decode()
        return result

    def get_hash(self):
        """
        The SHA-256 hash of the contents of the block

        :return: hash of this block
        :rtype str
        """
        block_data = self.prev_hash
        block_data += bytearray(struct.pack("f", self.time))
        block_data += self.user_id.encode()
        block_data += self.public_key.public_bytes(serialization.Encoding.X962,
                                                   serialization.PublicFormat.CompressedPoint)

        digest = hashes.Hash(hashes.SHA256())
        digest.update(block_data)
        return digest.finalize()


class VoteBlock(Block):
    def __init__(self, prev_hash: bytes, time: float, user_id: str, signature: str, choice: str):
        """
        A block announcing a registered voter's vote for a candidate

        :param prev_hash: The hash of the previous block
        :param time: The timestamp the block was created
        :param user_id: The user_id of the voting voter
        :param signature: The signature of the choice, made with voter's private key
        :param choice: The candidate the vote is cast for
        """
        super().__init__(prev_hash, time, user_id)
        self.signature = signature
        self.choice = choice

    def __dict__(self):
        """
        A dictionary representation of the block

        :return: dict of this block
        :rtype dict
        """
        result = {}
        result['block_type'] = 'vote'
        result['prev_hash'] = base64.b64encode(self.prev_hash).decode()
        result['timestamp'] = self.time
        result['user_id'] = self.user_id
        result['signature'] = self.signature
        result['choice'] = self.choice
        return result

    def get_hash(self):
        """
        The SHA-256 hash of the contents of the block

        :return: hash of this block
        :rtype str
        """
        block_data = self.prev_hash
        block_data += bytearray(struct.pack("!f", self.time))
        block_data += self.user_id.encode()
        block_data += self.signature.encode()
        block_data += self.choice.encode()

        digest = hashes.Hash(hashes.SHA256())
        digest.update(block_data)
        return digest.finalize()


class Blockchain:
    def __init__(self):
        """
        A blockchain, containing many linked Blocks
        """
        self.blocks = []

    def __dict__(self):
        d = {}
        for b in self.blocks:
            d[self.blocks.index(b)] = b.__dict__()
        return d

    def get_latest_hash(self):
        if len(self.blocks) > 0:
            return self.blocks[-1].get_hash()
        else:
            return bytes(0)

    def get_registration_block(self, user_id):
        """
        Finds a user's registration block

        :param user_id: The id attached to the block
        :return: the user's registration block
        :rtype RegisterBlock
        """
        for b in self.blocks:
            if type(b) == RegisterBlock and b.user_id == user_id:
                return b
        raise UserNotRegisteredError

    def register_user(self, user_id: str, password: str):
        """
        Registers a new voter

        :param user_id: The user_id of the new voter
        :param password: The voter's password, for key derivation
        :return: The block containing the new voter's registration
        :rtype RegisterBlock
        """
        # TODO: Implement hashing of previous block
        prev_hash = self.get_latest_hash()
        new_block = RegisterBlock(prev_hash, datetime.utcnow().timestamp(), user_id, password)
        for b in self.blocks:
            if b.user_id == user_id:
                raise UserAlreadyExistsError
        self.blocks.append(new_block)
        return new_block

    def cast_vote(self, user_id: str, password: str, choice: str):
        """
        Casts a voter's vote

        :param user_id: The user_id of the voter
        :param password: The user's password
        :param choice: The candidate choice of the voter
        :return: The block containing the voter's vote
        :rtype VoteBlock
        """

        # user_id is appended to password as salt
        user_private_key = Block.password_to_key(password+user_id)
        signature = user_private_key.sign(choice.encode(), ec.ECDSA(hashes.SHA256()))

        user_public_key = self.get_registration_block(user_id).public_key
        user_public_key.verify(signature, choice.encode(), ec.ECDSA(hashes.SHA256()))

        prev_hash = self.get_latest_hash()
        new_block = VoteBlock(prev_hash, datetime.utcnow().timestamp(), user_id, base64.b64encode(signature).decode(),
                              choice)
        self.blocks.append(new_block)
        return new_block
