# coding=utf-8
# !/usr/bin/env python
import json
import sys

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent, random, os
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour


class TravelerAgent(Agent):
    class Travel(Behaviour):

        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        config_file = BASE_DIR + 'agency_config.json'

        msg = None
        #agencies_counter = ConfigurationReader.number_of_agencies()
        offer_responses = 0
        offers = []

        ask_discount = random.choice([True, False])

        # Best results in Euro destinations
        destination = random.choice(['Europe', 'Australia', 'Asia', 'America'])

        budget = random.randint(1000, 50000)
        persons = random.randint(1, 5)

        discounts_asked = 0
        discounts_responded = 0
        discounts_responses = []

        def _process(self):
            self.msg = self._receive(True)
            if self.msg:
                request = json.loads(self.msg.content)
                if request['request_type'] == 'offer_response':

                    found_offer = False
                    self.offer_responses += 1
                    self.offers.append(request)

                    if self.offer_responses >= self.agencies_counter:
                        for offer in self.offers:
                            for o in offer["data"]:
                                if o["persons"] >= self.persons and o["price"] <= self.budget:
                                    found_offer = True
                                    if self.ask_discount:
                                        print "\nI asking for discount offer from agency %s" % offer["origin"]
                                        travel = {'request_type': 'discount_request', 'travel_id': o["name"]}

                                        # offer is OK so I'm asking for discount if agent wants discount
                                        self.send_message(json.dumps(travel), offer["origin"])
                                        self.discounts_asked += 1
                                        found_offer = True
                                    else:
                                        # agent doesnt want discount, so he books right away
                                        print "\nI accept offer from agency %s" % offer["origin"]
                                        book = {'request_type': 'make_booking', 'travel_id': o["name"]}
                                        self.send_message(json.dumps(book), offer["origin"])

                        if not found_offer:
                            print "Sorry.There is no offer I'd like to take.\n"
                            travel = {'request_type': 'not_found'}
                            self.send_message_all(json.dumps(travel))
                            sys.exit()

                if request['request_type'] == 'discount_response':

                    self.discounts_responded += 1
                    self.discounts_responses.append(request)
                    got_discount = False

                    discounts_got = []

                    if self.discounts_responded == self.discounts_asked:
                        for discount in self.discounts_responses:

                            if discount["discount_accepted"]:
                                got_discount = True
                                print "YAAY! I got discount %i for %s" % (
                                    discount["discount_amount"], discount["location"])
                                discounts_got.append(discount)

                        if not got_discount:
                            print "Sorry.There is no offer I'd like to take.\n"
                            travel = {'request_type': 'not_found'}
                            self.send_message_all(json.dumps(travel))
                            sys.exit()

                    # if there are multiple discounts got, then choose cheapest one
                    if len(discounts_got) > 0:
                        cheapest = None
                        lowest_price = 0

                        for dis in discounts_got:
                            if dis["discount_amount"] > lowest_price:
                                cheapest = dis

                        book = {'request_type': 'make_booking', 'travel_id': cheapest["location"]}
                        self.send_message(json.dumps(book), cheapest["origin"])

                if request['request_type'] == 'booking_confirmed':
                    print "Great!, I'm traveling to %s" % request['destination']

        def set_preferences(self):
            print "I'd like to go to %s" % self.destination
            print "My budget is  %i $ for %i persons" % (self.budget, self.persons)

            if self.ask_discount:
                print "I like discounts\n\n"
            else:
                print "I don't want discount\n\n"

            travel = {'request_type': 'travel_request', 'destination': self.destination}
            self.send_message_all(json.dumps(travel))

        def send_message_all(self, content):

            '''agencies_ids = ConfigurationReader.read_agency_id()
            for agency_id in agencies_ids:
                address = "agency%i@127.0.0.1" % agency_id
                agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])

                self.msg = ACLMessage()
                self.msg.setPerformative("inform")
                self.msg.setOntology("travel")
                self.msg.setLanguage("eng")
                self.msg.addReceiver(agent)
                self.msg.setContent(content)
                self.myAgent.send(self.msg)
                # print '\nMessage %s sent to %s' % (content, address)
            '''

        def send_message(self, content, address):

            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("travel")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)
            self.myAgent.send(self.msg)
            # print '\nMessage %s sent to %s' % (content, address)

    def _setup(self):
        print "\n Agent\t" + self.getAID().getName() + " is up"

        feedback_template = ACLTemplate()
        feedback_template.setOntology('travel')

        mt = MessageTemplate(feedback_template)
        settings = self.Travel()
        self.addBehaviour(settings, mt)
        settings.set_preferences()


if __name__ == '__main__':
    '''
        Agent feels like going somewhere (i.e Asia,Russia) and asks agencies to make an offer
        Ask for initial offer, then select based on current MOOD(price,distance)... and ask for discount, if right then accept offer and say tnx to other agencies
        '''
    TravelerAgent('traveler@127.0.0.1', 'traveler').start()