# Jack Walmsley 2020-12-02
import abc
from datetime import datetime

import struct

from cryptography.hazmat.primitives import serialization, hashes


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
    def get_hash(self):
        """
        The SHA-256 hash of the contents of the block

        :return: hash of this block
        :rtype str
        """
        return


class RegisterBlock(Block):
    def __init__(self, prev_hash: bytes, time: float, user_id: str, public_key: str):
        """
        A block announcing a voter's registration

        :param prev_hash: The hash of the previous block
        :param time: The timestamp the block was created
        :param user_id: The user_id of the new voter
        :param public_key: The public key of the new voter, derived from a password
        """
        super().__init__(prev_hash, time, user_id)
        pem_prefix = '-----BEGIN PUBLIC KEY-----\n'
        pem_suffix = '\n-----END PUBLIC KEY-----'
        pem_data = '{}{}{}'.format(pem_prefix, public_key, pem_suffix)
        self.public_key = serialization.load_pem_public_key(pem_data.encode())

    def get_hash(self):
        """
        The SHA-256 hash of the contents of the block

        :return: hash of this block
        :rtype str
        """
        block_data = self.prev_hash + struct.pack("!f", self.time) + self.user_id.encode() + self.public_key
        digest = hashes.Hash(hashes.SHA256())
        digest.update(block_data.encode())
        return digest.finalize()


class VoteBlock(Block):
    def __init__(self, prev_hash: bytes, time: float, user_id: str, signature: str, choice):
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
        # TODO: Verify signature based on public key in registration block
        self.choice = choice

    def get_hash(self):
        """
        The SHA-256 hash of the contents of the block

        :return: hash of this block
        :rtype str
        """
        block_data = self.prev_hash + struct.pack("!f", self.time) + self.user_id.encode() + self.signature.encode() + self.choice
        digest = hashes.Hash(hashes.SHA256())
        digest.update(block_data.encode())
        return digest.finalize()


class Blockchain:
    def __init__(self):
        """
        A blockchain, containing many linked Blocks
        """
        self.blocks = []
        self.registration_blocks = []

    def get_registration_block(self, user_id):
        """
        Finds a user's registration block

        :param user_id: The id attached to the block
        :return: the height of the user's registration block
        :rtype int
        """
        for b in self.blocks:
            if type(b) == RegisterBlock and b.user_id == user_id:
                return b

    def register_user(self, user_id: str, public_key: str):
        """
        Registers a new voter

        :param user_id: The user_id of the new voter
        :param public_key: The voter's public key, derived from password
        :return: The block containing the new voter's registration
        """
        # TODO: Implement hashing of previous block
        if len(self.blocks) > 0:
            prev_hash = self.blocks[-1].get_hash()
        else:
            prev_hash = 0
        new_block = RegisterBlock(prev_hash, datetime.utcnow().timestamp(), user_id, public_key)
        self.blocks.append(new_block)
        return new_block
