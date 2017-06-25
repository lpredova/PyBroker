# coding=utf-8
# !/usr/bin/env python
import json
import threading
import time
import uuid

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent, random
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour


class BrokerAgent(Agent):
    class Speculate(Behaviour):

        win_threshold = float(80000)
        ip = None
        name = None
        behaviour = None

        msg = None
        budget = None

        myStocks = []

        def initialize(self):
            self.ip = self.getName().split(" ")[0]
            self.name = self.getName().split(" ")[0].split("@")[0]
            self.budget = float(random.randint(10000, 50000))
            # self.behaviour = random.choice(['risky', 'passive', 'cautious'])
            self.behaviour = random.choice(['risky'])

            print 'Agent %s\nBudget: %d$\nBehaviour: %s' % (self.ip, self.budget, self.behaviour)

        def sign_in(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_sign_in',
                    'data': None,
                    'origin': self.ip
                }
            )
            stared_brokers.append(self.name)
            self.send_message_to_stock(msg_sign_in_to_stock_exchange)

        def evaluation_done(self):
            msg_evaluation_done = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'evaluation_done',
                    'data': None,
                    'origin': self.ip
                }
            )
            self.send_message_to_stock(msg_evaluation_done)

        def ask_for_report(self):
            msg_stock_exchange_report = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_report',
                    'data': None,
                    'origin': self.ip
                }
            )
            self.send_message_to_stock(msg_stock_exchange_report)

        def buy_stock(self, stock, number_of_stocks_to_buy):
            msg_stock_to_buy = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_buy',
                    'data': stock,
                    'origin': self.ip,
                    'stocksToBuy': number_of_stocks_to_buy
                }
            )
            self.send_message_to_stock(msg_stock_to_buy)

        def sell_stock(self, stock, number_of_stocks_to_sell):
            msg_stock_to_sell = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_sell',
                    'data': stock,
                    'origin': self.ip,
                    'stocksToSell': number_of_stocks_to_sell
                }
            )
            self.send_message_to_stock(msg_stock_to_sell)

        def declare_win(self):
            print "Agent %s WON!" % self.name
            msg_stock_win = json.dumps(
                {
                    'uuid': str(uuid.uuid4()),
                    'request_type': 'stock_win',
                    'data': None,
                    'origin': self.ip
                }
            )

            self.send_message_to_stock(msg_stock_win)

        def _process(self):
            if not (self.name in stared_brokers):
                self.initialize()
                self.sign_in()

            self.msg = self._receive(True)
            if self.msg:
                request = json.loads(self.msg.content)

                if request['request_type'] == 'stock_open':
                    self.ask_for_report()

                if request['request_type'] == 'stock_report_data':
                    self.evaluate_stock_state(request['data'])

                if request['request_type'] == 'stock_bought':
                    self.add_to_my_stocks(request)

                if request['request_type'] == 'stock_sold':
                    self.remove_from_my_stocks(request)

                if request['request_type'] == 'stock_share_change':
                    self.adjust_stock_prices(request)

                if request['request_type'] == 'stock_close':
                    print 'Agent %s stopped trading, Won %d$' % (self.ip, self.budget)
                    self.kill()

        def evaluate_stock_state(self, stock_data):
            print '\nAgent %s evaluating stock data...' % self.name
            took_action = False

            if self.budget >= self.win_threshold:
                self.declare_win()
                took_action = True

            else:
                stock_data = json.loads(stock_data)
                for stock in stock_data:
                    # buy or wait or sell
                    take_action_odds = random.randint(1, 100)
                    action = random.choice(['buy', 'sell', 'stale'])

                    if self.behaviour == 'risky':
                        # takes action in 80 % of cases
                        if take_action_odds < 80:
                            # spend max 40% of my money on this stock and buy all stocks"
                            if action == 'buy' and not self.check_if_i_own_stock(stock):
                                self.buy_stock_evaluation(40, stock)
                                took_action = True

                            elif action == 'sell' and self.check_if_i_own_stock(stock):
                                self.sell_stock_evaluation(stock)
                                took_action = True
                            else:
                                took_action = False

                    elif self.behaviour == 'cautious':
                        # takes action in 40 % of cases
                        if take_action_odds < 40:
                            # spend max 10% of my money on stock and buy only growing or stable"
                            if action == 'buy' \
                                    and not self.check_if_i_own_stock(stock) \
                                    and (stock['tendency'] == 'up'
                                         or stock['tendency'] == 'up fast'
                                         or stock['tendency'] == 'up slow'
                                         or stock['tendency'] == 'stale'):

                                self.buy_stock_evaluation(10, stock)
                                took_action = True

                            elif action == 'sell' \
                                    and self.check_if_i_own_stock(stock) \
                                    and (stock['tendency'] == 'down'
                                         or stock['tendency'] == 'down fast'
                                         or stock['tendency'] == 'down slow'):
                                self.sell_stock_evaluation(stock)
                                took_action = True
                            else:
                                took_action = False

                    elif self.behaviour == 'passive':
                        # takes action in 20 % of cases
                        if take_action_odds < 20:
                            # spend max 10% of my money on stock but rather pass buy all kinds of stocks"
                            if action == 'buy' and not self.check_if_i_own_stock(stock):

                                self.buy_stock_evaluation(40, stock)
                                took_action = True

                            elif action == 'sell' and self.check_if_i_own_stock(stock):
                                self.sell_stock_evaluation(stock)
                                took_action = True
                            else:
                                took_action = False

            if not took_action:
                print '\nAgent:%s\tNo action' % self.name

            self.print_money_status()
            self.evaluation_done()

        def buy_stock_evaluation(self, max_percentage, stock):

            if stock['numberOfStocks'] > 0:
                budget_percentage = (random.randint(1, max_percentage)) / float(100)
                money_to_spend = self.budget * budget_percentage

                number_of_stocks = money_to_spend / stock['price']
                print "\nAgent:%s\tTrying to buy %d of %s for %d$" % (
                    self.name, number_of_stocks, stock['name'], money_to_spend)

                self.buy_stock(stock, int(number_of_stocks))

        def sell_stock_evaluation(self, stock):
            if stock['numberOfStocks'] > 0:
                for s in self.myStocks:
                    if s['id'] == stock['id']:
                        print "\nAgent %s trying to sell %s" % (self.name, stock['name'])
                        self.sell_stock(stock, s['number'])

        def check_if_i_own_stock(self, stock):
            if len(self.myStocks) == 0:
                return False

            for myStock in self.myStocks:
                if myStock['id'] == stock['id']:
                    return True

            return False

        def check_if_double_transaction(self, transaction_id):
            for myStock in self.myStocks:

                if myStock['transaction'] == transaction_id:
                    return True

            return False

        def add_to_my_stocks(self, data):
            if not self.check_if_double_transaction(data['transactionsId']):
                self.myStocks.append({
                    'id': data['id'],
                    'transaction': data['transactionsId'],
                    'ip': data['origin'],
                    'price': data['price'],
                    'pricePerShare': data['price'] / float(data['amount']),
                    'number': data['amount'],
                })

                self.budget -= float(data['price'])
                print "\nAgent %s bought %d stock of %s for %d$\nMoney left: %d$" % (
                    self.name, data['amount'], data['name'], data['price'], self.budget)

        def remove_from_my_stocks(self, data):
            clean = []
            for stock in self.myStocks:
                if stock['id'] != data['id']:
                    clean.append(stock)

            self.myStocks = clean
            print "Agent:%s\t+%d$ to budget" % (self.name, float(data['price']))
            self.budget += float(data['price'])
            self.print_money_status()

        def print_money_status(self):
            print "\nAgent:%s\tTotal:%d$" % (self.name, self.budget)

        def adjust_stock_prices(self, data):
            for stock in self.myStocks:
                if stock['id'] == data['id']:
                    stock['pricePerShare'] = data['price']
                    stock['price'] = stock['number'] * stock['pricePerShare']

        def send_message_to_stock(self, content):
            stock_address = 'stock@127.0.0.1'
            agent = spade.AID.aid(name=stock_address, addresses=["xmpp://%s" % stock_address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)

            self.myAgent.send(self.msg)

            # print '\nMessage %s sent to %s' % (content, stock_address)

    def _setup(self):
        stock_template = ACLTemplate()
        stock_template.setOntology('stock')

        mt = MessageTemplate(stock_template)
        settings = self.Speculate()
        self.addBehaviour(settings, mt)


brokers = ['broker1', 'broker2']
stared_brokers = []


def start_broker(broker_name):
    ip = '%s@127.0.0.1' % broker_name
    agent = BrokerAgent(ip, broker_name)
    agent.start()


if __name__ == '__main__':
    for broker in brokers:
        threading.Thread(target=start_broker, args=[broker]).start()
        time.sleep(1.5)
