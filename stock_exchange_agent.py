# coding=utf-8
# !/usr/bin/env python
import json
import random
import string
import sys
import uuid

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import Behaviour, ACLTemplate


class StockExchange(Agent):
    class OpenStockExchange(Behaviour):

        ip = None
        msg = None
        brokers = 0
        brokers_total = 0

        round = 0
        evaluation = 0

        stocks = []

        def initialize(self):
            self.ip = self.getName().split(" ")[0]
            self.stocks = self.stock_generate()
            self.brokers_total = len(brokers)

        # Sends signal that stock exchange is opened for business
        def open_stock_exchange(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_open',
                    'data': None,
                    'origin': self.ip
                }
            )

            self.broadcast_message(msg_sign_in_to_stock_exchange)

        # Sends stock exchange state to brokers
        def send_stock_exchange_report(self, origin_ip):
            msg_sign_in_to_stock_exchange = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_report_data',
                    'data': json.dumps(self.stocks),
                    'origin': self.ip
                }
            )

            self.send_message(msg_sign_in_to_stock_exchange, origin_ip)

        # Sends stock exchange state to brokers
        def broadcast_stock_exchange_report(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_report_data',
                    'data': json.dumps(self.stocks),
                    'origin': self.ip
                }
            )

            self.broadcast_message(msg_sign_in_to_stock_exchange)

        # Informs owner that his stock has changed price
        def inform_owner_change(self, stock, origin_ip):
            msg_owner_share_change = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_share_change',
                    'data': json.dumps(stock),
                    'origin': self.ip
                }
            )

            self.send_message(msg_owner_share_change, origin_ip)

        def send_buy_confirmation(self, stock, origin_ip, price, amount, transaction):
            msg_owner_buy_confirm = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_bought',
                    'data': json.dumps(stock),
                    'origin': self.ip,
                    'price': price,
                    'amount': amount,
                    'transactionsId': transaction
                }
            )

            self.send_message(msg_owner_buy_confirm, origin_ip)

        def send_sell_confirmation(self, stock, origin_ip, price, amount):
            msg_owner_sell_confirm = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_sold',
                    'data': json.dumps(stock),
                    'origin': self.ip,
                    'price': price,
                    'amount': amount

                }
            )

            self.send_message(msg_owner_sell_confirm, origin_ip)

        # Closes stock exchange, we have our winner
        def send_close_stock_exchange(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_close',
                    'data': None,
                    'origin': self.ip
                }
            )

            self.broadcast_message(msg_sign_in_to_stock_exchange)
            self.kill()

        def _process(self):
            self.initialize()
            self.msg = self._receive(True)

            if self.msg:
                request = json.loads(self.msg.content)

                # Registering brokers to start stock exchange
                if request['request_type'] == 'stock_sign_in':
                    self.brokers += 1
                    print "Broker %s signed in %d/%d" % (request['origin'], self.brokers, self.brokers_total)

                    # All brokers are registrated
                    if self.brokers == self.brokers_total:
                        print "Opening stock exchange..."
                        self.open_stock_exchange()

                # Collect round status from agents
                if request['request_type'] == 'evaluation_done':
                    self.evaluation += 1
                    print "Broker %s done with move round %d status: %d/%d" % (
                        request['origin'], self.round + 1, self.evaluation, self.brokers_total)

                    if self.evaluation == self.brokers_total:
                        # Round is over, send new report
                        self.round += 1
                        self.evaluation = 0
                        self.stock_speculate()
                        self.broadcast_stock_exchange_report()

                # Get stock report
                if request['request_type'] == 'stock_report':
                    self.send_stock_exchange_report(request['origin'])

                # Buy stock
                if request['request_type'] == 'stock_buy':
                    self.buy_stock(request)

                # Sell stock
                if request['request_type'] == 'stock_sell':
                    self.sell_stock(request)

                # Declare winner and close the stock exchange
                if request['request_type'] == 'stock_win':
                    print "Broker %s got rich. Closing stock exchange..." % request['origin']
                    self.send_close_stock_exchange()

        def broadcast_message(self, message):
            for broker in brokers:
                address = "%s@127.0.0.1" % broker
                agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
                self.msg = ACLMessage()
                self.msg.setPerformative("inform")
                self.msg.setOntology("stock")
                self.msg.setLanguage("eng")
                self.msg.addReceiver(agent)
                self.msg.setContent(message)
                self.myAgent.send(self.msg)
                print '\nMessage %s sent to %s' % (message, address)

        def send_message(self, message, address):
            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(message)
            self.myAgent.send(self.msg)
            print '\nMessage %s sent to %s' % (message, address)

        # Initialize stocks
        def stock_generate(self):
            result = []
            number_of_stocks = random.randint(3, 5)
            for i in range(0, number_of_stocks):
                price = random.randint(10, 1000)
                result.append(
                    {
                        'id': i + 1,
                        'name': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)),
                        'price': price,
                        'numberOfStocks': 10000,
                        'totalValue': 10000 * price,
                        'tendency': random.choice(
                            ['up', 'down', 'stale', 'up fast', 'up slow', 'down fast', 'down slow']),
                        'owners': []
                    }
                )

            return result

        # Method that allows trading certain amounts of stocks
        def buy_stock(self, data):
            price = data['stocksToBuy'] * data['data']['price']
            self.stock_add_owner(data['data'], price, data['stocksToBuy'], data['origin'])
            print "Agent %s bought %d shares of:%s for %d$" % (
                data['origin'], data['stocksToBuy'], data['data']['name'], price)

        def sell_stock(self, data):
            price = data['stocksToSell'] * data['data']['price']
            self.stock_remove_owner(data['data'], price, data['origin'])
            print "%s sold %d shares %s for %d" % (data['origin'], data['stocksToSell'], data['data']['name'], price)

        # Method that changes prices of generated stocks according with tendency
        def stock_speculate(self):
            for stock in self.stocks:
                delta = 0
                if stock['tendency'] == 'up':
                    # % of change
                    change_percentage = random.randint(1, 5) / float(100)
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta

                if stock['tendency'] == 'down':
                    # % of change
                    change_percentage = random.randint(1, 5) / float(100)
                    delta = stock['price'] * change_percentage
                    stock['price'] -= delta

                if stock['tendency'] == 'stale':
                    # % of change
                    change_percentage = random.randint(0, 1) / float(100)
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta

                if stock['tendency'] == 'up slow':
                    # % of change
                    change_percentage = random.randint(5, 10) / float(100)
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta

                if stock['tendency'] == 'up fast':
                    # % of change
                    change_percentage = random.randint(10, 50) / float(100)
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta

                if stock['tendency'] == 'down slow':
                    # % of change
                    change_percentage = random.randint(10, 50) / float(100)
                    delta = stock['price'] * change_percentage
                    stock['price'] -= delta

                if stock['tendency'] == 'down fast':
                    # % of change
                    change_percentage = random.randint(10, 50) / float(100)
                    delta = stock['price'] * change_percentage
                    stock['price'] -= delta

                stock['totalValue'] = stock['numberOfStocks'] * stock['price']
                print stock, delta

                self.increase_owner_shares(stock, delta)

        def increase_owner_shares(self, stock, delta):
            if len(stock) > 0:
                for owner in stock['owners']:
                    owner['price'] = owner['price'] + delta
                    owner['totalPrice'] = owner['totalPrice'] * owner['numberOfShares']
                    self.inform_owner_change(stock, owner['ip'])

        def stock_add_owner(self, stock, total_price, shares, ip):
            for old_stock in self.stocks:
                if old_stock['id'] == stock['id']:
                    old_stock['numberOfStocks'] -= shares
                    owners = old_stock['owners']
                    transaction = random.randint(1, 100000)
                    print transaction
                    owners.append({
                        'transactionId': transaction,
                        'ip': ip,
                        'price': total_price,
                        'shares': shares,
                    })

                    old_stock['owners'] = owners
                    self.send_buy_confirmation(old_stock, ip, total_price, shares, transaction)
                    return transaction

        def stock_remove_owner(self, stock, shares, ip):
            for old_stock in self.stocks:
                if old_stock['id'] == stock['id']:
                    old_stock['shares'] += shares

                    owners = old_stock['owners']
                    new = []
                    for o in owners:
                        if o['ip'] != ip:
                            new.append(o)

                    old_stock['owners'] = new

    def _setup(self):
        print "\nVAS Stock exchange\t%s\tis up" % self.getAID().getAddresses()

        template = ACLTemplate()
        template.setOntology('stock')

        behaviour = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(self.OpenStockExchange(), behaviour)


brokers = ['broker1', 'broker2']

if __name__ == "__main__":
    try:
        StockExchange('stock@127.0.0.1', 'stock').start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
