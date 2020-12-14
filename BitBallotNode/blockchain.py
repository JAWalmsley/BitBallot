# Jack Walmsley 2020-12-02
import abc
import struct
import base64
from datetime import datetime

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

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
        pem_data = public_key
        # pem_prefix = '-----BEGIN PUBLIC KEY-----\n'
        # pem_suffix = '\n-----END PUBLIC KEY-----'
        # pem_data = '{}{}{}'.format(pem_prefix, public_key, pem_suffix)
        self.public_key: rsa.RSAPublicKey = serialization.load_pem_public_key(pem_data.encode())

    def get_hash(self):
        """
        The SHA-256 hash of the contents of the block

        :return: hash of this block
        :rtype str
        """
        block_data = self.prev_hash
        block_data += bytearray(struct.pack("f", self.time))
        block_data += self.user_id.encode()
        block_data += self.public_key.public_bytes(serialization.Encoding.PEM,
                                                   serialization.PublicFormat.SubjectPublicKeyInfo)

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

    def register_user(self, user_id: str, public_key: str):
        """
        Registers a new voter

        :param user_id: The user_id of the new voter
        :param public_key: The voter's public key, derived from password
        :return: The block containing the new voter's registration
        """
        # TODO: Implement hashing of previous block
        prev_hash = self.get_latest_hash()
        new_block = RegisterBlock(prev_hash, datetime.utcnow().timestamp(), user_id, public_key)
        for b in self.blocks:
            if b.user_id == user_id:
                raise UserAlreadyExistsError
        self.blocks.append(new_block)
        return new_block

    def cast_vote(self, user_id: str, signature: str, choice: str):
        """
        Casts a voter's vote

        :param user_id: The user_id of the voter
        :param signature: base64 format. The singature of the choice, made with voter's private key
        :param choice: The candidate choice of the voter
        :return: The block containing the voter's vote
        """
        pad = padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        )

        prev_hash = self.get_latest_hash()
        public_key = self.get_registration_block(user_id).public_key
        public_key.verify(base64.urlsafe_b64decode(signature), choice.encode(), pad, hashes.SHA256())
        new_block = VoteBlock(prev_hash, datetime.utcnow().timestamp(), user_id, signature, choice)
        self.blocks.append(new_block)
        return new_block
