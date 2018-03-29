# -*- coding: utf-8 -*-

"""
Date: 2018-03-27 21:59:01
Last modified: 2018-03-27 21:59:01
Author: YJ - yj1516268@outlook.com

"""

import json
import time
import hashlib
from uuid import uuid4
from flask import Flask, jsonify, request


class BlockChain(object):
    """
    用于管理区块链，能存储交易、加入新块等
    """
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # 创建创世区块
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, previous_hash, proof):
        """
        生成新的区块
        :param previous_hash: (Optional) <str> 前区块的Hash值
        :param proof: <int> 工作量证明   # 由校验算法给出的校验值
        :return: <dict> 新区块
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }   # 区块索引、Unix时间戳、交易列表、工作量证明、前区块Hash值

        # 重置当前交易列表
        self.current_transactions = []

        # 新区块添加到链
        self.chain.append(block)
        return block

    def new_transactions(self, sender, recipient, amount):
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> 发送人地址
        :param recipient: <str> 接收人地址
        :param amount: <int> 数量
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append(
            {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            }
        )   # 向列表中添加一条交易记录

        # 返回该记录将被添加到的区块（下一个待挖区块），用于用户提交交易时
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        生成区块的 SHA-256 Hash值
        :param block: <dict> 区块
        :return: <str>
        """
        # 必须确保字典的有序性，否则会产生不一致的Hash值
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # 返回最后一个区块
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        工作量证明算法
        :param last_proof: <iint>
        :return: <int>
        查找一个 p' 使得 hash(pp') 以 1516 开头
        p 是上一个区块的证明，p' 是当前的证明
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证：是否 hash(last_proof, proof) 以 1516 开头
        :param last_proof: <int> 上一个区块的证明
        :param proof: <int> 当前区块的证明
        :return: <bool> 开头是否 1516 的bool值
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "1516"


# 实例化节点
app = Flask(__name__)
# 为节点生成唯一地址
node_identifier = str(uuid4()).replace('_', ' ')
# 实例化区块链
blockchain = BlockChain()


@app.route("/mine", methods=["GET"])
def mine():
    # 通知服务器挖掘新的区块
    return "We'll mine a new Block"


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    # 创建一个交易并添加到区块
    values = request.get_json()

    required = ['sender', 'x']
    return "We'll add a new transaction"


@app.route("/chain", methods=["GET"])
def full_chain():
    # 返回整个区块链
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
