# coding=utf-8
# !/usr/bin/env python
import json
import sys
import threading
import time

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent, random
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour


class BrokerAgent(Agent):
    class Speculate(Behaviour):

        win_threshold = 100000
        ip = None
        name = None
        behaviour = None

        msg = None
        budget = None

        myStocks = []

        def initialize(self):
            self.ip = self.getName().split(" ")[0]
            self.budget = random.randint(10000, 50000)
            self.behaviour = random.choice(['risky', 'passive', 'cautious'])

            print 'Agent %s\nBudget: %d$' % (self.ip, self.budget)

        def sign_in(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {
                    'request_type': 'stock_sign_in',
                    'data': None,
                    'origin': self.ip
                }
            )

            self.send_message_to_stock(msg_sign_in_to_stock_exchange)

        def ask_for_report(self):
            msg_stock_exchange_report = json.dumps(
                {
                    'request_type': 'stock_report',
                    'data': None,
                    'origin': self.ip
                }
            )
            self.send_message_to_stock(msg_stock_exchange_report)

        def buy_stock(self, stock, number_of_stocks_to_sell):
            msg_stock_to_buy = json.dumps(
                {
                    'request_type': 'stock_buy',
                    'data': stock,
                    'origin': self.ip,
                    'stocksToSell': number_of_stocks_to_sell
                }
            )
            self.send_message_to_stock(msg_stock_to_buy)

        def declare_win(self):
            msg_stock_win = json.dumps(
                {
                    'request_type': 'stock_win',
                    'data': None,
                    'origin': self.ip
                }
            )

            self.send_message_to_stock(msg_stock_win)

        def _process(self):
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
                    # self.evaluate_stock_state(request['data'])
                    pass

                if request['request_type'] == 'stock_sold':
                    # self.evaluate_stock_state(request['data'])
                    pass

                if request['request_type'] == 'stock_close':
                    print 'Agent %s stopped trading, Won %d$' % (self.ip, self.budget)
                    self.kill()

        def evaluate_stock_state(self, stock_data):
            if self.budget >= self.win_threshold:
                self.declare_win()

            else:
                for stock in stock_data:
                    # buy or wait or sell
                    take_action_odds = random.randint(0, 100)
                    action = random.choice(['buy', 'sell', 'stale'])

                    if self.behaviour == 'risky':
                        # takes action in 80 % of cases
                        if take_action_odds < 80:
                            # spend max 40% of my money on this stock and buy all stocks"
                            if action == 'buy' and not self.check_if_i_own_stock(stock):
                                self.buy_stock_evaluation(40, stock)

                            if action == 'sell' and self.check_if_i_own_stock(stock):
                                self.sell_stock_evaluation(40, stock)

                    if self.behaviour == 'cautious':
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

                            if action == 'sell' \
                                    and self.check_if_i_own_stock(stock) \
                                    and (stock['tendency'] == 'down'
                                         or stock['tendency'] == 'down fast'
                                         or stock['tendency'] == 'down slow'):
                                self.sell_stock_evaluation(10, stock)

                    if self.behaviour == 'passive':
                        # takes action in 20 % of cases
                        if take_action_odds < 20:
                            # spend max 10% of my money on stock but rather pass buy all kinds of stocks"
                            if action == 'buy' and not self.check_if_i_own_stock(stock):
                                self.buy_stock_evaluation(40, stock)

                            if action == 'sell' and self.check_if_i_own_stock(stock):
                                self.sell_stock_evaluation(40, stock)

                self.declare_win()

        def buy_stock_evaluation(self, max_percentage, stock):

            if stock['numberOfStocks'] > 0:
                budget_percentage = random.randint(0, max_percentage) / 100
                money_to_spend = self.budget * budget_percentage

                number_of_stocks = money_to_spend % stock['price']
                self.buy_stock(stock, number_of_stocks)

        def sell_stock_evaluation(self, max_percentage, stock):
            print "sell stock, if not direct offer from another agent then selling price will be loer"

        def check_if_i_own_stock(self, stock):
            for myStock in self.myStocks:
                if myStock['id'] == stock['id']:
                    return True

            return False

        def send_message_to_agent(self, content):

            # for agency_id in agencies_ids:
            address = "broker%i@127.0.0.1" % 1
            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])

            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)
            self.myAgent.send(self.msg)
            # print '\nMessage %s sent to %s' % (content, address)

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

    def _setup(self):
        stock_template = ACLTemplate()
        stock_template.setOntology('stock')

        mt = MessageTemplate(stock_template)
        settings = self.Speculate()
        self.addBehaviour(settings, mt)


def start_broker(broker_id):
    try:
        ip = "broker%i@127.0.0.1" % broker_id
        agency_name = "broker%i" % broker_id

        agent = BrokerAgent(ip, agency_name)
        agent.start()

    except Exception, e:
        print e


if __name__ == '__main__':

    brokers = [1]
    for broker in brokers:
        try:
            threading.Thread(target=start_broker(broker), args=None).start()
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        except Exception, e:
            print "\nError while starting broker!"
            print e.message
